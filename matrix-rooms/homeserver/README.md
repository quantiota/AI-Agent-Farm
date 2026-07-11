# homeserver — standalone Synapse for the federation Matrix rooms

Self-contained Synapse + Postgres stack for the project rooms. **Farm-level, not part of
the AI Agent Lab** — the lab only ships the `matrix-nio` client dependency. Put a TLS
reverse proxy in front and serve `.well-known` delegation so the identity suffix
(`@user:<server_name>`) can differ from the host that actually runs Synapse.

## Files

| file | role |
|---|---|
| `docker-compose.yaml` | Synapse (`matrixdotorg/synapse`) + Postgres (`postgres:16-alpine`, C-locale collation) |
| `configure-homeserver.py` | after `generate`, points the DB at Postgres and closes registration (invite-only) |
| `.env.example` | `SYNAPSE_SERVER_NAME` — the **irreversible** identity suffix |

## Bring it up

The current image does **not** generate config on-the-fly, so `generate` is an explicit step:

```bash
cp .env.example .env          # then edit SYNAPSE_SERVER_NAME (irreversible)
docker compose run --rm synapse generate
python3 configure-homeserver.py synapse-data/homeserver.yaml
docker compose up -d
```

Create accounts (registration is closed, so admin-registers):

```bash
docker compose exec synapse register_new_matrix_user \
  -u microserver01 -p '<password>' --no-admin \
  -c /data/homeserver.yaml http://localhost:8008
```

## TLS + delegation (reverse proxy)

Synapse listens on `8008` (plaintext). Terminate TLS at nginx and, if `server_name` differs
from the host, publish delegation so other servers/clients find it.

`https://matrix.<domain>` vhost — proxy the Matrix paths, **no SSO** (Matrix uses its own tokens):

```nginx


# HTTPS server to handle Matrix (Synapse homeserver)
# NOTE: deliberately NO Authelia — Matrix clients (Element) and server-to-server
# federation authenticate with their OWN access tokens; SSO-gating /_matrix would
# break login and federation. This vhost is public, guarded by Matrix's own auth.
server {
    client_max_body_size 50M;
    listen 443 ssl;
    server_name matrix.${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;
    add_header Strict-Transport-Security max-age=15768000;

    # Matrix client-server + federation-client API → Synapse (no SSO gate here)
    location ~ ^(/_matrix|/_synapse/client) {
        resolver 127.0.0.11 valid=10s;
        set $upstream_synapse synapse;
        proxy_pass http://$upstream_synapse:8008;

        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_http_version 1.1;
        client_max_body_size 50M;   # media uploads
        proxy_buffering off;
    }

    # Cert validation only
    location ~ /.well-known {
        allow all;
    }
}

```

Delegation — served at `https://<server_name>/.well-known/matrix/server` so
`@user:<server_name>` resolves to `matrix.<domain>` ("the MX record for Matrix"):

```json
{ "m.server": "matrix.<domain>:443" }
```

And `.../.well-known/matrix/client` for clients:

```json
{ "m.homeserver": { "base_url": "https://matrix.<domain>" } }
```

## Notes

- `synapse-data/` (bind mount) holds `homeserver.yaml`, the signing key and generated
  secrets — **do not commit it**; add it to `.gitignore`.
- Prototype passwords are weak by design — rotate before real use.
- Validated on `quantiota.net` (the existing lab instance) with a wildcard cert; the
  production identity is `microserver.network`.
