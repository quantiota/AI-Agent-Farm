
## Readme

This file contains the Nginx configuration for a server that handles HTTPS requests for three subdomains: **hub.domain.tld**, **database.domain.tld**, and **dashboard.domain.tld**.

The first server block redirects all HTTP traffic to HTTPS by sending a 302 redirect response to the client's request.

The second and third server blocks handle HTTPS requests for JupyterHub and QuestDB, respectively. Each server block contains an SSL certificate, protocols, ciphers, and other security-related parameters.

The **location /** block in the JupyterHub server block handles requests to the JupyterHub front end. It is set to proxy all requests to the specified address **http://127.0.0.1:8000** and manages websocket headers.

The **location ~ /.well-known** block in the JupyterHub server block handles requests for verifying Let's Encrypt host.

Note that this is the configuration file for the **sites-available/default** file in the **/etc/nginx** directory. To activate these server blocks, the **default** file must be symlinked to the **sites-enabled/** directory.