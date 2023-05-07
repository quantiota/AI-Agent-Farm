## Readme


### Docker

This [Tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04) provides a step-by-step guide on how to install and use Docker Community Edition (CE) on an Ubuntu 22.04 server. The tutorial assumes that the server has been set up by following the Ubuntu 22.04 initial server setup guide, and includes a sudo non-root user and a firewall. Additionally, it is recommended to have an account on Docker Hub if you want to create your own images and push them to Docker Hub.

In the first step, the tutorial explains how to install Docker from the official Docker repository instead of the Ubuntu repository to ensure that the latest version is installed. The process involves updating the list of packages, installing prerequisite packages that let apt use packages over HTTPS, adding the GPG key for the official Docker repository, adding the Docker repository to APT sources, updating the list of packages again, and finally installing Docker. The tutorial then checks that Docker is installed, the daemon started, and the process enabled to start on boot, and shows how to confirm that Docker is running.

In the second step (optional), the tutorial explains how to execute the Docker command without sudo by adding the user to the docker group. By default, the docker command can only be run by the root user or by a user in the docker group, which is automatically created during Docker's installation process. If the user attempts to run the docker command without being in the docker group, they will receive an error message. The tutorial shows how to add the user to the docker group and how to confirm that the user has been added.

Finally, the tutorial explains how to work with containers and images, and push an image to a Docker repository. It covers topics such as running a container, accessing a container, listing containers, starting and stopping containers, removing containers, creating images, and pushing images to a Docker repository. The tutorial provides examples and commands for each topic, making it easy for users to follow along and practice.


### Docker Compose

This [Guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-22-04)  provides a step-by-step explanation of how to install Docker Compose on Ubuntu 22.04 and how to use it to set up multi-container application environments. Before getting started, you will need access to an Ubuntu 22.04 local machine or development server as a non-root user with sudo privileges, and Docker installed on your server or local machine.

The guide begins with an introduction to Docker Compose, a tool used to run multi-container application environments based on definitions set in a YAML file. It then goes on to explain how to install Docker Compose by downloading the most updated stable version of Docker Compose from its official Github repository and setting the correct permissions to make the docker compose command executable. The guide also provides instructions on how to verify the installation was successful by running the docker compose version command.

After installing Docker Compose, the guide explains how to set up a docker-compose.yml file to create a web server environment using the official Nginx image from Docker Hub. This containerized environment will serve a single static HTML file. The guide provides instructions on how to create a new directory, set up an application folder to serve as the document root for the Nginx environment, create a new index.html file within the app folder, and create the docker-compose.yml file.

The docker-compose.yml file typically starts off with the version definition, followed by the services block, where you set up the services that are part of this environment. In this case, a single service called web is used, which uses the nginx:alpine image and sets up a port redirection with the ports directive. All requests on port 8000 of the host machine will be redirected to the web container on port 80, where Nginx will be running. The volumes directive creates a shared volume between the host machine and the container, which shares the local app folder with the container.


