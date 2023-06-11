## Nginx configuration for the GPU Server 

This file contains the Nginx configuration for a server that handles HTTPS requests for three subdomains: **hub.domain.tld**, **database.domain.tld**, and **dashboard.domain.tld**.

The first server block redirects all HTTP traffic to HTTPS by sending a 302 redirect response to the client's request.

The second and third server blocks handle HTTPS requests for JupyterHub and QuestDB, respectively. Each server block contains an SSL certificate, protocols, ciphers, and other security-related parameters.

The **location /** block in the JupyterHub server block handles requests to the JupyterHub front end. It is set to proxy all requests to the specified address **http://127.0.0.1:8000** and manages websocket headers.

The **location ~ /.well-known** block in the JupyterHub server block handles requests for verifying Let's Encrypt host.

Note that this is the configuration file for the **sites-available/default** file in the **/etc/nginx** directory. To activate these server blocks, the **default** file must be symlinked to the **sites-enabled/** directory.


### SSL/TLS certificates for your website using Certbot and the NGINX web server.

1. Add the Certbot PPA repository:
sudo add-apt-repository ppa:certbot/certbot

2. Install Certbot:
sudo apt-get install certbot

3. Stop NGINX:
sudo systemctl stop nginx

4. Generate SSL/TLS certificates:
certbot certonly --standalone
(Note: Ensure that NGINX is not running in parallel during this step)

5. Follow the prompts and provide the required information to generate the certificate.

6. Once the certificate is generated, restart NGINX:
sudo systemctl start nginx

7. Your website should now be accessible via HTTPS.

Note: Certbot will automatically renew your certificates when they are about to expire, but you can also set up a cron job to automate the renewal process.

```
sudo add-apt-repository ppa:certbot/certbot 
sudo apt-get install certbot
sudo systemctl stop nginx
certbot certonly --standalone 
sudo systemctl start nginx

```


### OpenSSL DH Parameters


This command generates Diffie-Hellman parameters using OpenSSL.

#### Prerequisites

You'll need to have OpenSSL installed on your system before running this command. If you don't already have it, you can install it using your package manager. For example, on Ubuntu you can run:
```
sudo apt-get update
sudo apt-get install openssl
```

#### Generating DH Parameters

To generate Diffie-Hellman parameters, run the following command:

```
openssl dhparam -out dhparam.pem 4096
```

This will generate a file called **dhparam.pem** containing Diffie-Hellman parameters with a key length of 4096 bits. You can adjust the key length to your needs.


#### Usage

Once you've generated your DH parameters, you can use them in your web server configuration to enable Perfect Forward Secrecy (PFS) for your SSL/TLS connections. The exact process will depend on your web server and configuration, but generally you'll need to:

1. Copy the **dhparam.pem** file to a location accessible by your web server  **/etc/ssl/certs/** .
2. Update your web server configuration to point to the **dhparam.pem** file.
3. Restart your web server to apply the changes.

By using DH parameters, you can ensure that your SSL/TLS connections are more secure and resistant to certain types of attacks.

## QuestDB Authentication with Nginx

Create a Username and Password with the command

```
sudo htpasswd -c /usr/local/etc/nginx.htpasswd questdb  

```


## Nginx configuration for the Microserver

The Nginx configuration file for each Microserver is designed to handle HTTPS requests for a specific server and proxy them to different backend applications. It includes SSL/TLS settings, Let's Encrypt certificate management, and specific location blocks for proxying requests to the VS Code frontend, QuestDB, and Grafana. The configuration ensures secure communication, sets appropriate headers, and enables websocket support.


