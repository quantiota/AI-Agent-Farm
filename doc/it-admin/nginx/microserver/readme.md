
## Readme


The standalone configuration file **/etc/nginx/sites-available/default** is used to handle HTTP and HTTPS traffic for multiple domains **(vscode.domain.tld, questdb.domain.tld, and grafana.domain.tld)**. It includes server blocks for each domain, each specifying SSL/TLS encryption, SSL certificates, and proxying requests to backend servers.

The configuration starts by redirecting HTTP traffic to HTTPS for all domain names. It then sets up the HTTPS server blocks for VS Code, Questdb, and Grafana, respectively.

For VS Code **(vscode.domain.tld)**, the server block proxies requests to the backend server running on **http://127.0.0.1:8000**, sets the necessary headers for proxying and WebSocket communication, and allows access to /.well-known for Let's Encrypt host verification.

For Questdb **(questdb.domain.tld)**, the server block proxies requests to the backend server running on **http://127.0.0.1:9000**, enables directory listing, adds basic authentication using .htpasswd, and allows access to /.well-known for Let's Encrypt host verification.

For Grafana **(grafana.domain.tld)**, the server block proxies requests to the backend server running on **http://127.0.0.1:3000** and allows access to **/.well-known** for Let's Encrypt host verification.

Each server block includes SSL/TLS configuration directives such as SSL protocols, ciphers, session cache, OCSP stapling, and the **Strict-Transport-Security** header for enforcing secure connections.

Overall, this configuration file ensures secure communication, proxies requests to backend servers, and allows Let's Encrypt host verification for the specified domains.