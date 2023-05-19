## Readme

To conduct the benchmark for the AI Agent Farm with separate metric sets for microservers and the GPU server, please find the specification below:

**1. Benchmark Objective:**

The objective of the benchmark is to measure the performance and scalability of the AI Agent Farm infrastructure when running machine learning notebooks on each microserver for several hours, with dedicated GPUs. The benchmark will assess the system's ability to handle multiple tasks simultaneously, distribute the workload effectively across the workers, and monitor performance using Prometheus with separate metric sets for microservers and the GPU server.

**2.  Benchmark Setup:**

a. Hardware Configuration:
Ensure that each microserver in the AI Agent Farm has a dedicated GPU, as per the infrastructure specifications.
Set up Prometheus to monitor metrics from both the microservers and the GPU server.

b. Software Configuration:

Install the required software stack on each microserver and the GPU server, including the operating system (Ubuntu 22.04 Server), JupyterHub, machine learning frameworks (e.g., TensorFlow, PyTorch), and any other necessary dependencies.
Configure Prometheus to collect relevant performance metrics from both the microservers and the GPU server.

c. Machine Learning Notebooks:

Prepare a set of machine learning notebooks or tasks that represent real-world scenarios or workload requirements.
Ensure that the notebooks utilize the dedicated GPU resources on each microserver effectively.


**3.  Benchmark Execution:**

a. Start the benchmark by launching the machine learning notebooks on each microserver simultaneously.
b. Monitor the benchmark progress and collect performance metrics using Prometheus, separately for the microservers and the GPU server.
c. Monitor key metrics such as GPU utilization, memory usage, CPU usage, task completion rates, and system uptime for both the microservers and the GPU server.
d. Collect data at regular intervals throughout the benchmark duration (e.g., every 5 minutes).
e. Allow the machine learning notebooks to run for several hours to simulate a realistic workload scenario.

**4.  Benchmark Metrics:**

a. Microserver Metrics:
GPU Utilization: Measure the percentage of GPU resources utilized by each microserver during the benchmark.
Memory Usage: Monitor the memory usage on each microserver to ensure it remains within acceptable limits.
CPU Usage: Measure the CPU usage on each microserver to evaluate the system's processing capabilities.
Task Completion Rates: Calculate the rate at which tasks are completed by the machine learning notebooks running on each microserver.
System Uptime: Monitor the system uptime of each microserver to ensure stability and reliability.

b. GPU Server Metrics:

GPU Utilization: Measure the overall GPU utilization across all microservers during the benchmark.
Memory Usage: Monitor the memory usage on the GPU server to ensure it remains within acceptable limits.
CPU Usage: Measure the CPU usage on the GPU server to evaluate the system's processing capabilities.
Task Completion Rates: Calculate the combined rate at which tasks are completed by all the machine learning notebooks running on the microservers.
System Uptime: Monitor the system uptime of the GPU server to ensure stability and reliability.


**5. Benchmark Analysis:**


a. Analyze the collected metrics separately for the microservers and the GPU server to evaluate their performance and scalability.

b. Assess the GPU utilization, memory usage, and CPU usage for both the microservers and the GPU server to identify any bottlenecks or performance issues.

c. Evaluate the task completion rates to measure the efficiency and effectiveness of workload distribution across the microservers.

d. Consider the system uptime of both the microservers and the GPU server to gauge the stability and reliability of the infrastructure.

Benchmark Report:
Create a comprehensive report documenting the benchmark
