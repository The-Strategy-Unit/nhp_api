import json
import logging

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

import config


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    container_id = req.route_params.get("id")

    client = ContainerInstanceManagementClient(
        DefaultAzureCredential(), config.SUBSCRIPTION_ID
    )
    resource_group = "nhp_containers"

    container = (
        client.container_groups.get(resource_group, container_id)
        .containers[0]
        .instance_view.current_state
    )

    if container.state == "Terminated" and container.detail_status == "Completed":
        client.container_groups.begin_delete(resource_group, container_id)

    return func.HttpResponse(
        json.dumps(container.as_dict()), mimetype="application/json"
    )
