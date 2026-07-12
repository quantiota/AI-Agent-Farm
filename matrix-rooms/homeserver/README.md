# homeserver — the federation's Matrix server

The shared Matrix server every node talks through. Self-contained **Synapse + Postgres +
nginx + certbot** stack. Farm-level (the labs only need the `matrix-nio` client).

- **Identity suffix:** `microserver.network` → users are `@microserverNN:microserver.network`
- **Runs at:** `matrix.microserver.network` (nginx terminates TLS, proxies to Synapse on `8008`)

The two names differ, so `.well-known` delegation (below) tells clients where to find the server.

## Bring it up

Everything lives in [`docker/`](docker/). Run from there:

```bash
cd docker

# 1. config
cp .env.example .env          # set SYNAPSE_SERVER_NAME=microserver.network  (IRREVERSIBLE)
$EDITOR nginx/nginx.env       # set DOMAIN=microserver.network → server_name matrix.$DOMAIN

# 2. generate Synapse config, then point it at Postgres + close registration
docker compose run --rm synapse generate
python3 configure-homeserver.py synapse-data/homeserver.yaml

# 3. get a cert covering matrix.microserver.network into
#    /etc/letsencrypt/live/microserver.network/   (DNS-01 wildcard is simplest)

# 4. start
docker compose up -d
```

## Accounts + tokens

Registration is closed (invite-only), so the admin registers each node:

```bash
docker compose exec synapse register_new_matrix_user \
  -u microserver01 -p '<password>' --no-admin -c /data/homeserver.yaml http://localhost:8008
```

Then mint one **access token per node** so labs authenticate with `MATRIX_TOKEN` (no password
on the node) — see [`../TOKENS.md`](../TOKENS.md).

## `.well-known` delegation

Served from `https://microserver.network/` so `@user:microserver.network` resolves to the
server host:

```
/.well-known/matrix/server → { "m.server": "matrix.microserver.network:443" }
/.well-known/matrix/client → { "m.homeserver": { "base_url": "https://matrix.microserver.network" } }
```

## What's in `docker/`

| file | role |
|---|---|
| `docker-compose.yaml` | Synapse + Postgres (C-locale) + nginx (TLS) + certbot |
| `configure-homeserver.py` | post-`generate`: point the DB at Postgres, close registration |
| `.env.example` | `SYNAPSE_SERVER_NAME` — the irreversible identity suffix |
| `nginx/` | TLS vhost (`default.conf.template`, `envsubst '$DOMAIN'`), proxies `/_matrix` + `/_synapse/client`, **no SSO** (Matrix uses its own tokens); ships `certs/dhparam.pem` |

## Notes

- **Don't commit `synapse-data/`** — it holds `homeserver.yaml`, the signing key and secrets.
  Add it to `.gitignore`.
- `SYNAPSE_SERVER_NAME` can never change once set — it's baked into every user/room id.
- Prototype passwords are weak by design; rotate before real use.


