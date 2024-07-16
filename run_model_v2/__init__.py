"""API endpoint for running the NHP Model

"""

import json
import logging
import re
import zlib
from datetime import datetime

import azure.functions as func
from azure.core.exceptions import ResourceExistsError
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

    params = req.get_json()
    if "id" in params:
        params.pop("id")
    params["create_datetime"] = f"{datetime.now():%Y%m%d_%H%M%S}"

    metadata = {
        k: str(v)
        for k, v in params.items()
        if not isinstance(v, dict) and not isinstance(v, list)
    }
    params["app_version"] = metadata["app_version"] = req.params.get(
        "app_version", "latest"
    )

    params = json.dumps(params)
    metadata["id"] = _generate_id(params, metadata)

    logging.info(
        "received request for model run %s (%s)",
        metadata["id"],
        metadata["app_version"],
    )

    credential = DefaultAzureCredential()

    # 1. upload params to blob storage
    _upload_params_to_blob(params, metadata, credential)

    # 2. create a new container instance
    _create_and_start_container(metadata, credential)

    return func.HttpResponse(json.dumps(metadata), mimetype="application/json")


def _generate_id(params: str, metadata: dict) -> str:
    crc32 = f"{zlib.crc32(params.encode('utf-8')):x}"
    scenario_sanitized = re.sub("[^a-z0-9]+", "-", metadata["scenario"])
    # id needs to be of length 1-63, but the last 9 characters are a - and the hash
    return (f"{metadata['dataset']}-{scenario_sanitized}"[0:54] + "-" + crc32).lower()


def _upload_params_to_blob(
    params: dict, metadata: dict, credential: DefaultAzureCredential
) -> None:
    client = BlobServiceClient(config.STORAGE_ENDPOINT, credential)
    container = client.get_container_client("queue")
    try:
        container.upload_blob(f"{metadata['id']}.json", params, metadata=metadata)
        logging.info("params uploaded to queue")
    except ResourceExistsError:
        logging.warning("file already exists, skipping upload")


def _create_and_start_container(
    metadata: dict, credential: DefaultAzureCredential
) -> None:
    model_id = metadata["id"]
    tag = metadata["app_version"]

    client = ContainerInstanceManagementClient(credential, config.SUBSCRIPTION_ID)

    container_resource_requests = ResourceRequests(
        memory_in_gb=config.CONTAINER_MEMORY, cpu=config.CONTAINER_CPU
    )
    container_resource_requirements = ResourceRequirements(
        requests=container_resource_requests
    )

    container = Container(
        name=model_id,
        image=f"{config.CONTAINER_IMAGE}:{tag}",
        resources=container_resource_requirements,
        command=["/opt/docker_run.py", f"{model_id}.json"],
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
    logging.info("container created with command: %s", " ".join(container.command))
