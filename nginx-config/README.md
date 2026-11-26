
# nginx-config — the Farm's single entry from the Internet

The Farm has one public IP address. The router forwards its port 443 to the **nginx server**, a Dell R210 II. Its `stream.conf` reads the name each connection asks for, such as `vscode.microserver01.net`, **without decrypting it**, and forwards the connection to the node that owns the name. Every node keeps its own certificates.

| file | runs on | role |
|---|---|---|
| `stream.conf` | the nginx server (R210 II) | SNI passthrough on `:443`: one line per node (`~\.microserverNN\.net$` → its IP), and one for the Matrix homeserver (`~\.microserver\.network$`) |

Each node runs the AI Agent Lab unchanged, with the Lab's own nginx and its certificates, one per subdomain: see the [AI Agent Lab](https://github.com/quantiota/AI-Agent-Lab) repository.

## Install (on the nginx server)

```bash
# 1. the file
sudo mkdir -p /etc/nginx/streams-enabled
sudo cp stream.conf /etc/nginx/streams-enabled/stream.conf

# 2. one line at the top level of /etc/nginx/nginx.conf, outside http { }:
#      include /etc/nginx/streams-enabled/*.conf;

# 3. test and reload
sudo nginx -t && sudo systemctl reload nginx
```

Then forward the router's port 443 to the nginx server's local IP address.

## Adding a node

Add its line to the map in `stream.conf`, for example:

```nginx
~\.microserver17\.net$   <its host IP>:443;
```

then test and reload (step 3).

The book *How to Build the AI Agent Farm with Claude Code* describes this entry in Chapter 11: <https://www.amazon.com/dp/B0HNQ2KCQB>.
