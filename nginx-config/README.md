# Farm Networking

Two nginx configs, one per layer. One public IP fronts every lab.

| file | runs on | role |
|------|---------|------|
| `stream.conf` | **GPU server** | SNI router on `:443` — reads the TLS hostname and forwards each lab's domain to its microserver, terminating nothing. |
| `default.conf.template` | **each lab** (in its docker stack) | the lab's own nginx — terminates its own wildcard cert for `${DOMAIN}` and serves `vscode/questdb/grafana/aiagentui/gradio/auth.${DOMAIN}`, all behind Authelia SSO. |

`${DOMAIN}` is substituted per lab (e.g. `microserver01.tld`), so `vscode.${DOMAIN}` →
`vscode.microserver01.tld`. The domain matches the microserver.

## Flow

```
internet → GPU server :443  (stream.conf, SNI passthrough)
   ├─ *.microserver01.tld → 192.168.1.15 → lab nginx (default.conf, own cert) → docker services
   └─ default            → :8443         → local hub.gpuserver.tld services
```

## Issue the wildcard cert (lab)

```bash
docker compose -f init.yaml run --rm certbot certonly --manual --preferred-challenges dns \
    -d "*.$DOMAIN" -d "$DOMAIN"
```

Prompts for the two `_acme-challenge.$DOMAIN` **TXT** records (one for `*.$DOMAIN`, one for the
apex `$DOMAIN`). Renew with `docker compose run certbot renew`.

## Install `stream.conf` (GPU server)

```bash
# 1. add the SNI router at nginx.conf top level (stream{} must be OUTSIDE http{};
#    appending puts it after the http{} block = top level)
cat stream.conf | sudo tee -a /etc/nginx/nginx.conf

# 2. move the existing http server blocks off :443 (the router now owns :443)
sudo sed -i 's/listen 443 ssl/listen 8443 ssl/' /etc/nginx/sites-available/default

# 3. test + reload
sudo nginx -t && sudo nginx -s reload
```
