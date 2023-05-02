
This installation [guide](https://devopscube.com/install-configure-prometheus-linux/) provides step-by-step instructions to manually install Prometheus on a server with administrator access, creating a monitoring system. 

the first step is to update the package repositories and download the latest Prometheus binary from the official website. 

Then, create a Prometheus user, required directories, and copy the Prometheus binary files to the appropriate location. 

The next step is to move the console and console_libraries directories and create a configuration file with the appropriate settings. 

After that, a service file needs to be created and the Prometheus service started. To access the Prometheus UI, you can use the URL with the IP address of the Prometheus server and port number 9090. 

Finally, you can register the target in the prometheus.yml file to scrape metrics and set up the Node Exporter to collect system metrics.
