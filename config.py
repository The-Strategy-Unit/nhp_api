"""Configuration values"""

# pylint: disable=line-too-long

import os

import dotenv

dotenv.load_dotenv()

STORAGE_ACCOUNT = os.environ["STORAGE_ACCOUNT"]
# TODO: eventually, replace STORAGE_ENDPOINT with the below
# STORAGE_ENDPOINT = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net"
STORAGE_ENDPOINT = os.environ["STORAGE_ENDPOINT"]
SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]
CONTAINER_IMAGE = os.environ["CONTAINER_IMAGE"]
AZURE_LOCATION = os.environ["AZURE_LOCATION"]
SUBNET_NAME = os.environ["SUBNET_NAME"]
SUBNET_ID = os.environ["SUBNET_ID"]
REGISTRY_USERNAME = os.environ["REGISTRY_USERNAME"]
REGISTRY_PASSWORD = os.environ["REGISTRY_PASSWORD"]
USER_ASSIGNED_IDENTITY = os.environ["USER_ASSIGNED_IDENTITY"]

CONTAINER_MEMORY = os.environ["CONTAINER_MEMORY"]
CONTAINER_CPU = os.environ["CONTAINER_CPU"]

AUTO_DELETE_COMPLETED_CONTAINERS = bool(os.getenv("AUTO_DELETE_COMPLETED_CONTAINERS"))

RESOURCE_GROUP = os.environ["RESOURCE_GROUP"]
