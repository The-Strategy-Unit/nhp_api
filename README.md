# nhp_api

This repository is a set of [Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview?pivots=programming-language-python) for managing [Azure Container Instances](https://azure.microsoft.com/en-gb/products/container-instances) (ACI).

Specifically, when we want to start a model run, our Posit Connect server needs to be able to start a container instance.
However, because the connect server is public, giving the ability to directly start containers from this server is a security risk.
These functions are intended to sit between the connect server and ACI; the connect server will make a request to one of the Function endpoints, which in turn will manage container instances.

# deployment

Functions are deployed to Azure Functions via GitHub actions - commiting to the `main` branch will trigger a deployment.
