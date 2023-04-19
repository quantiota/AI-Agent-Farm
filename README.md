# AI Agent Farm


## Infrastructure
This repository documents the creation and maintenance of an AI Agent Farm infrastructure that consists of refurbished microservers gen8. Each microserver is equipped with a 250GB SSD, 16GB of RAM, and 4x1TB of RAID data storage for analysis. The infrastructure runs on Ubuntu 22.04 and includes powerful tools, such as Visual Studio Code (vscode), QuestDB, Grafana, and AutoGPT.

The purpose of this project is to create a scalable infrastructure that can run multiple tasks simultaneously and distribute processes across the AI Agent workers, maximizing efficiency and minimizing downtime.


### Infrastructure Diagrams



### Features
- The AI Agents can run multiple tasks simultaneously, and processes are distributed across the workers for maximum efficiency.

- The AI Agent Farm is designed to be scalable to accomodate future growth

- Vscode is remotely connected to a JupyterHub instance installed on a GPU server, providing access to Python and Julia kernels. Each AI Agent has its own JupyterHub user account when using vscode.

- The real-time streaming data source from Coinbase is connected to each microserver. QuestDB and Grafana are used to store and display the data in real-time. The QuestDB database is ingested by running a notebook in Visual Studio Code (VS Code).

- To ensure data integrity, both the QuestDB database backup and the workspace backup for each AI agent are stored on the GPU server.

### Scalability
The AI Agent Farm has been designed with scalability in mind, ensuring that it can accommodate future growth without any issues. Whether the demand for AI agents increases tenfold or hundredfold, the system is well-equipped to meet it, thanks to JupyterHub. JupyterHub is capable of supporting more than 100 users, making it an ideal tool for managing large-scale AI projects.

### Dockerization
The four applications used in this project (vscode, QuestDB, Grafana, and AutoGPT) can be Dockerized to simplify deployment and management. The Dockerfiles for each application are included in the repository, and instructions for building and running the Docker containers are provided in the documentation. By Dockerizing the applications, it is possible to create a self-contained environment that can be easily moved between systems or replicated on multiple machines. This can simplify deployment and ensure consistency across different environments.

### Backup
To ensure data integrity and prevent data loss, it is important to create regular backups of the QuestDB database and the AI Agent workspace on the remote GPU server.The backup process can be automated using a shell script, which can be scheduled to run regularly using a cron job. 

### Failover & Remote Management system
The AI Agent Farm also includes failover and load balancing functions to ensure high availability and prevent downtime. In addition, a remote management system is provided to enable easy monitoring and control of the infrastructure from anywhere even without a public IP. 

## AI Application Specifications:
The AI application is responsible for managing the AI agents installed on the microservers and distributing tasks to them. The application is installed on a GPU server and is designed to maximize the efficiency of the AI Agent Farm.

The AI application is built using Python and is designed to work with the JupyterHub instance running on the GPU server. The application is modular and allows for easy integration with new AI tools and libraries as needed.

The AI application consists of several modules, including:

1. Data Ingestion Module: This module is responsible for coordinating the ingestion of real-time streaming data from Coinbase across all AI agents and storing it on the RAID storage of each microserver. Each AI agent is responsible for ingesting and storing data in its own QuestDB database. The module includes features such as data validation, error handling, and data transformation to prepare the data for analysis by the AI agents.

2. Task Distribution Module: This module is responsible for distributing tasks to the AI agents installed on the microservers. The module takes into account the processing power and workload of each AI agent and distributes tasks accordingly to maximize efficiency and minimize downtime. The module is designed to handle multiple tasks simultaneously and can be configured to prioritize certain tasks over others based on their importance or urgency.

3. Performance Monitoring Module: This module monitors the performance of each AI agent and the overall performance of the AI Agent Farm. The module collects metrics such as CPU and memory usage, task completion rates, and system uptime, which are then displayed on the Grafana dashboard. The module can be configured to send alerts if performance falls below certain thresholds or if critical errors occur.

## Others

### Contributing
Contributions to the project are welcome. Please feel free to fork the repository and submit pull requests.

### Licence
This project is licensed under the MIT License.

### Conclusion
The AI Agent Farm is a powerful infrastructure for running multiple AI tasks simultaneously, and distributing them across the workers for maximum efficiency. By dockerizing the applications and automating the backup process, the infrastructure is easy to deploy and manage, and data integrity is ensured. With its scalability and powerful tools, the AI Agent Farm is an essential tool for any AI project.

## References

- HP ProLiant MicroServer Gen8 Review. [StorageReview.com](https://www.storagereview.com/review/hp-proliant-microserver-gen8-review)

- [JupyterHub](https://jupyter.org/hub)

- [JupyterHub Installation Guide](https://jupyterhub.readthedocs.io/en/1.2.0/installation-guide-hard.html)

- Connect to a JupyterHub from Visual Studio Code. [Jupyter Blog](https://blog.jupyter.org/connect-to-a-jupyterhub-from-visual-studio-code-ed7ed3a31bcb)

- [Visual Studio Code](https://code.visualstudio.com/)

- [QuestDB - The Fastest Open Source Time Series Database](https://questdb.io/)

- [Grafana - The open observability platform](https://grafana.com/)

- [Auto-GPT](https://github.com/Significant-Gravitas/Auto-GPT)

- [Teltonika Networks RMS](https://teltonika-networks.com/products/rms)
