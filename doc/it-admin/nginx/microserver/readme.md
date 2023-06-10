
## Readme


The standalone configuration file **/etc/nginx/sites-available/default** is used to handle HTTP and HTTPS traffic for multiple domains **(vscode.domain.tld, questdb.domain.tld, and grafana.domain.tld)**. It includes server blocks for each domain, each specifying SSL/TLS encryption, SSL certificates, and proxying requests to backend servers.

The configuration starts by redirecting HTTP traffic to HTTPS for all domain names. It then sets up the HTTPS server blocks for VS Code, Questdb, and Grafana, respectively.

For VS Code **(vscode.domain.tld)**, the server block proxies requests to the backend server running on **http://127.0.0.1:8080**, sets the necessary headers for proxying and WebSocket communication, and allows access to /.well-known for Let's Encrypt host verification.

For Questdb **(questdb.domain.tld)**, the server block proxies requests to the backend server running on **http://127.0.0.1:9000**, enables directory listing, adds basic authentication using .htpasswd, and allows access to /.well-known for Let's Encrypt host verification.

For Grafana **(grafana.domain.tld)**, the server block proxies requests to the backend server running on **http://127.0.0.1:3000** and allows access to **/.well-known** for Let's Encrypt host verification.

Each server block includes SSL/TLS configuration directives such as SSL protocols, ciphers, session cache, OCSP stapling, and the **Strict-Transport-Security** header for enforcing secure connections.

Overall, this configuration file ensures secure communication, proxies requests to backend servers, and allows Let's Encrypt host verification for the specified domains.

When the microserver and the GPU server are in the same network, you can use a single configuration file on the GPU server to handle the incoming traffic for both servers. Ckeck the GPU Server section of the nginx folder.

In such a scenario, you would typically install Nginx on the GPU server and configure it to act as a reverse proxy for both the microserver and the GPU server itself. The Nginx configuration file would include server blocks for each domain or service, specifying the appropriate proxy_pass directives to forward the requests to the corresponding backend servers.

You can combine the configuration from the microserver and GPU server into a single file, ensuring that the necessary proxy_pass, SSL/TLS, and other directives are set correctly for each domain or service. This consolidated configuration file would then be used on the GPU server to handle the traffic for both servers.

By using a single configuration file on the GPU server, you can simplify the setup and maintenance process, as well as manage the incoming traffic efficiently for both the microserver and the GPU server within the same network.