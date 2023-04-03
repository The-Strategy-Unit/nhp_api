"""API endpoint for running the NHP Model

"""
import logging

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (
    Container,
    ContainerGroup,
    ContainerGroupIdentity,
    ContainerGroupSubnetId,
    ImageRegistryCredential,
    OperatingSystemTypes,
    ResourceRequests,
    ResourceRequirements,
)
from azure.storage.blob import BlobServiceClient

import config


def main(req: func.HttpRequest) -> func.HttpResponse:
    """main api endpoint"""
    model_id = req.get_json()["id"]
    params = req.get_body()

    logging.info("received request for model run: %s", model_id)

    credential = DefaultAzureCredential()

    # 1. upload params to blob storage
    _upload_params_to_blob(model_id, params, credential)

    # 2. create a new container instance
    _create_and_start_container(model_id, credential)

    return func.HttpResponse(f"submitted {model_id}")


def _upload_params_to_blob(
    model_id: str, params: dict, credential: DefaultAzureCredential
) -> None:
    client = BlobServiceClient(config.STORAGE_ENDPOINT, credential)
    container = client.get_container_client("queue")
    container.upload_blob(f"{model_id}.json", params)
    logging.info("params uploaded to queue")


def _create_and_start_container(
    model_id: str, credential: DefaultAzureCredential
) -> None:
    client = ContainerInstanceManagementClient(credential, config.SUBSCRIPTION_ID)

    container_resource_requests = ResourceRequests(memory_in_gb=2.5, cpu=4)
    container_resource_requirements = ResourceRequirements(
        requests=container_resource_requests
    )

    container = Container(
        name=model_id,
        image=config.CONTAINER_IMAGE,
        resources=container_resource_requirements,
        command=f"/opt/docker_run.py {model_id}.json",
    )

    image_registry_credentials = [
        ImageRegistryCredential(
            server=f"{config.REGISTRY_USERNAME}.azurecr.io",
            username=config.REGISTRY_USERNAME,
            password=config.REGISTRY_PASSWORD,
        )
    ]

    subnet = ContainerGroupSubnetId(id=config.SUBNET_ID, name=config.SUBNET_NAME)

    identity = ContainerGroupIdentity(
        type="UserAssigned",
        user_assigned_identities={config.USER_ASSIGNED_IDENTITY: {}},
    )

    cgroup = ContainerGroup(
        identity=identity,
        location=config.AZURE_LOCATION,
        containers=[container],
        os_type=OperatingSystemTypes.linux,
        image_registry_credentials=image_registry_credentials,
        restart_policy="Never",
        subnet_ids=[subnet],
    )

    client.container_groups.begin_create_or_update(
        "nhp_containers", f"{model_id}", cgroup
    )
    logging.info("container created with command: %s", container.command)
