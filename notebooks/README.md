

## Readme

### Dual GPU

In a typical GPU server, it's common to have multiple GPUs, usually ranging from 4 to 8, depending on the configuration. 

The Tesla K80 GPUs have dual GPU dies per card, allowing you to effectively double the number of microservers without needing an additional GPU server. 

By utilizing the dual GPUs in each Tesla K80 card, you can allocate one GPU to each microserver, increasing the number of connected microservers and enabling parallel processing of AI tasks.

### One GPU per microserver

If each microserver is running only one machine learning notebook and doesn't require parallel processing or shared GPU resources, a Tesla K80 GPU with dual GPU dies can still be suitable. 

By dedicating one GPU from the Tesla K80 to each microserver, you can run a single machine learning notebook on each microserver without additional GPUs. 

This simplifies resource allocation and management, allowing each microserver to operate independently with its dedicated GPU for running the notebook. With a Tesla K80 GPU, you can achieve the goal of running one machine learning notebook per microserver while efficiently utilizing available GPU resources without the need for a second GPU server.