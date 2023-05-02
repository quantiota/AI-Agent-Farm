## Readme

### Prometheus

This installation [guide](https://devopscube.com/install-configure-prometheus-linux/) provides step-by-step instructions to manually install Prometheus on a server with administrator access, creating a monitoring system. 

the first step is to update the package repositories and download the latest Prometheus binary from the official website. 

Then, create a Prometheus user, required directories, and copy the Prometheus binary files to the appropriate location. 

The next step is to move the console and console_libraries directories and create a configuration file with the appropriate settings. 

After that, a service file needs to be created and the Prometheus service started. To access the Prometheus UI, you can use the URL with the IP address of the Prometheus server and port number 9090. 

Finally, you can register the target in the prometheus.yml file to scrape metrics and set up the Node Exporter to collect system metrics.

### Prometheus Node Expoter

This [guide](https://devopscube.com/monitor-linux-servers-prometheus-node-exporter/) explains how to install and set up Prometheus Node Exporter on a Linux server to export all node-level metrics to the Prometheus server. 

Before beginning the process, it is required to have the Prometheus server up and running and the port 9100 opened in the server firewall. 

The installation process includes downloading the latest node exporter package, unpacking it, moving the node export binary to /usr/local/bin, creating a custom node exporter service, and configuring the server as a target on the Prometheus server. 

The guide also provides the necessary commands to execute these steps. After installation, the node exporter would be exporting metrics on port 9100, which can be viewed by visiting the server URL on /metrics. 

Finally, this guide suggests querying node-related metrics using the Prometheus expression browser and visualizing node exporter metrics in Grafana.

### Integrate And Visualize Prometheus Metrics In Grafana
