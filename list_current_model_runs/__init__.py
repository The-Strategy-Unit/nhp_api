"""List all active model runs (containers)"""

import json
import logging

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

import config


def main(req: func.HttpRequest) -> func.HttpResponse:  # pylint: disable=unused-argument
    """main api endpoint"""
    logging.info("listing all active model runs")

    client = ContainerInstanceManagementClient(
        DefaultAzureCredential(), config.SUBSCRIPTION_ID
    )
    resource_group = config.RESOURCE_GROUP

    containers = {
        i.name: _get_container_group_instance_state(i.name, client, resource_group)
        for i in client.container_groups.list_by_resource_group(resource_group)
    }
    return func.HttpResponse(json.dumps(containers), mimetype="application/json")


def _get_container_group_instance_state(
    container_group_name: str,
    client: ContainerInstanceManagementClient,
    resource_group: str,
) -> dict:
    container = (
        client.container_groups.get(resource_group, container_group_name)
        .containers[0]
        .instance_view.current_state
    )

    if (
        config.AUTO_DELETE_COMPLETED_CONTAINERS
        and container.state == "Terminated"
        and container.detail_status == "Completed"
    ):
        client.container_groups.begin_delete(resource_group, container_group_name)

    return container.as_dict()
