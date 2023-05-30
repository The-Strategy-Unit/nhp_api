"""Configuration values"""
# pylint: disable=line-too-long

import os

import dotenv

dotenv.load_dotenv()

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