# homeserver — standalone Synapse for the federation Matrix rooms

Self-contained Synapse + Postgres + nginx stack for the project rooms. **Farm-level, not part
of the AI Agent Lab** — the lab only ships the `matrix-nio` client dependency. nginx (in the
compose, standard `envsubst '$DOMAIN'` pattern) terminates TLS; serve `.well-known` delegation
so the identity suffix (`@user:microserver.network`) can differ from the host that runs Synapse
(`matrix.microserver.network`).

## Files

The stack lives in [`docker/`](docker/) (same layout as the AI Agent Lab's `docker/`):

| file | role |
|---|---|
| `docker/docker-compose.yaml` | Synapse (`matrixdotorg/synapse`) + Postgres (`postgres:16-alpine`, C-locale collation) + **nginx** (TLS/reverse-proxy) + **certbot** |
| `docker/configure-homeserver.py` | after `generate`, points the DB at Postgres and closes registration (invite-only) |
| `docker/.env.example` | `SYNAPSE_SERVER_NAME` — the **irreversible** identity suffix |
| `docker/nginx/nginx.conf` | base nginx config (stock; `include`s `conf.d/*.conf` in `http{}`) |
| `docker/nginx/conf.d/default.conf.template` | matrix vhost, rendered by the nginx service (`envsubst '$DOMAIN'` → `default.conf`); proxies `/_matrix` + `/_synapse/client` to `synapse:8008`, **no SSO** |
| `docker/nginx/nginx.env` | `DOMAIN` fed to the envsubst → `server_name matrix.${DOMAIN}` |
| `docker/nginx/certs/dhparam.pem` | DH params for the TLS vhost (public, shipped) |

## Bring it up

The current image does **not** generate config on-the-fly, so `generate` is an explicit step:

```bash
cd docker
cp .env.example .env               # SYNAPSE_SERVER_NAME (irreversible)
# edit nginx/nginx.env             # DOMAIN, so server_name = matrix.$DOMAIN

docker compose run --rm synapse generate
python3 configure-homeserver.py synapse-data/homeserver.yaml

# nginx needs a cert covering matrix.microserver.network in /etc/letsencrypt/live/microserver.network/
#   (DNS-01 wildcard is simplest; or webroot via the .well-known mount).
#   dhparam.pem already ships in nginx/certs/.

docker compose up -d
```

Create accounts (registration is closed, so admin-registers):

```bash
docker compose exec synapse register_new_matrix_user \
  -u microserver01 -p '<password>' --no-admin \
  -c /data/homeserver.yaml http://localhost:8008
```

## TLS + delegation

Synapse listens on `8008` (internal, `expose`d not published). The **nginx service** fronts it
with TLS — the vhost is [`docker/nginx/conf.d/default.conf.template`](docker/nginx/conf.d/default.conf.template),
rendered at container start by `envsubst '$DOMAIN'` (`DOMAIN` from `nginx/nginx.env`) into
`server_name matrix.${DOMAIN}`. It proxies `/_matrix` + `/_synapse/client` to `synapse:8008` and
deliberately carries **no Authelia** — Matrix clients and server-to-server federation use their
own access tokens, so SSO-gating `/_matrix` would break login and federation.

Before the nginx service can start it needs a cert for `matrix.microserver.network` in
`/etc/letsencrypt/live/microserver.network/` (the `certbot` service + the `.well-known` mount, or a
DNS-01 wildcard). `nginx/certs/dhparam.pem` already ships.

Delegation — served at `https://microserver.network/.well-known/matrix/server` so
`@user:microserver.network` resolves to `matrix.microserver.network` ("the MX record for Matrix"):

```json
{ "m.server": "matrix.microserver.network:443" }
```

And `.../.well-known/matrix/client` for clients:

```json
{ "m.homeserver": { "base_url": "https://matrix.microserver.network" } }
```

## Notes

- `synapse-data/` (bind mount) holds `homeserver.yaml`, the signing key and generated
  secrets — **do not commit it**; add it to `.gitignore`.
- Prototype passwords are weak by design — rotate before real use.
- Production identity is `microserver.network`; the server runs at `matrix.microserver.network`.
  (First validated end-to-end on a prototype instance.)
