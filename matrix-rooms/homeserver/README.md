# homeserver — the federation's Matrix server

Synapse + Postgres + nginx + certbot. Runs at `matrix.microserver.network`; node
identities are `@microserverNN:microserver.network`.

The stack is in [`docker/`](docker/). Run everything from there:

```bash
cd docker
```

## 1. Configure

```bash
cp .env.example .env
```

`SYNAPSE_SERVER_NAME=microserver.network` is already set — it's the identity suffix in
every user/room id and is **irreversible** once step 2 runs.

## 2. Generate Synapse config

```bash
docker compose run --rm synapse generate
python3 configure-homeserver.py synapse-data/homeserver.yaml
```

`generate` writes the signing key and secrets; `configure-homeserver.py` then points the
database at Postgres and closes registration (invite-only).

## 3. Wildcard certificate

Create a wildcard cert for `*.microserver.network` (DNS-01) so nginx finds it at
`/etc/letsencrypt/live/microserver.network/`.

## 4. Start

```bash
docker compose up -d
```

## 5. Create accounts

Registration is closed, so the admin registers each account. Make the admin first — token
minting (step 6) needs it:

```bash
# admin
docker compose exec synapse register_new_matrix_user \
  -u admin -p '<password>' --admin -c /data/homeserver.yaml http://localhost:8008

# each node 01–08
docker compose exec synapse register_new_matrix_user \
  -u microserver01 -p '<password>' --no-admin -c /data/homeserver.yaml http://localhost:8008
```

## 6. Mint node tokens

Each lab authenticates with an access token (`MATRIX_TOKEN`) — no password on the node.
See [`TOKENS.md`](TOKENS.md).



