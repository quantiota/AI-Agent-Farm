### Installation

This installation [guide](https://github.com/jupyterhub/jupyterhub-the-hard-way/blob/HEAD/docs/installation-guide-hard.md) provides step-by-step instructions to manually install JupyterHub and JupyterLab on a server with administrator access, creating a shared computing environment. 

The guide explains how to set up a virtual environment, install required packages, create configurations, and set up JupyterHub to run as a system service using Systemd. 

Additionally, the guide explains how to set up a shared conda environment, allowing users to create their private conda environments. The default JupyterHub Authenticator is used, which authenticates system users using PAM to access their home folder. 

The guide also highlights the benefits of using system-provided packages wherever possible. 

The guide is tested on Ubuntu 18.04, and the instructions can be used for other Linux distributions like Ubuntu 22.04.

Use the nginx confiuration file to complete the installation