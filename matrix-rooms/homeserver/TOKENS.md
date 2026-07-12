# Minting node access tokens

Each fleet node authenticates to the homeserver with an **access token** — no password. The
operator mints one token per node account (`@microserver01`–`08`) from the homeserver and puts
it in that node's lab `.env` as `MATRIX_TOKEN`.

## 1. Get an admin token

Log in as `admin` once. From the homeserver box the public domain **NAT-hairpins**, so force it
to the local nginx with `--resolve` (or run this from your laptop, where it just resolves):

```bash
curl -s --resolve matrix.microserver.network:443:127.0.0.1 -XPOST \
  https://matrix.microserver.network/_matrix/client/v3/login \
  -d '{"type":"m.login.password","identifier":{"type":"m.id.user","user":"admin"},"password":"ADMIN_PW"}'
```

Copy the `access_token` from the response:

```bash
export ADMIN_TOKEN=syt_…
```

## 2. Mint the 8 node tokens

The admin API (`/_synapse/admin`) is **not** proxied by the public nginx (deliberate — it stays
private), so hit Synapse **directly** on the docker network:

```bash
SYN=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' matrix-homeserver-synapse-1)

for n in 01 02 03 04 05 06 07 08; do
  tok=$(curl -s -XPOST http://$SYN:8008/_synapse/admin/v1/users/@microserver$n:microserver.network/login \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
  echo "microserver$n  MATRIX_TOKEN=$tok"
done
```

Prints all 8, one per node.

## 3. Distribute

Put each token in its own node's lab `.env`:

```
MATRIX_HOMESERVER=https://matrix.microserver.network
MATRIX_USER=@microserver0N:microserver.network
MATRIX_TOKEN=syt_…
```

The listener/`matrix_send.py` authenticate with the token via `restore_login` — no password on any
node. Tokens are revocable server-side per node (invalidate one without touching the others).

