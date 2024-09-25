from typing import Generator

import pytest
from kubernetes.dynamic import DynamicClient
from ocp_resources.namespace import Namespace
from ocp_resources.resource import get_client

from tests.trustyai.utils.minio import MinioPod, MinioService, MinioSecret


@pytest.fixture(scope="session")
def admin_client() -> DynamicClient:
    return get_client()


@pytest.fixture(scope="class")
def model_namespace(request, admin_client: DynamicClient) -> Namespace:
    with Namespace(
        client=admin_client,
        name=request.param["name"],
    ) as ns:
        ns.wait_for_status(status=Namespace.Status.ACTIVE, timeout=120)
        yield ns


@pytest.fixture(scope="class")
def minio_pod(admin_client: DynamicClient, model_namespace: Namespace) -> Generator[MinioPod]:
    with MinioPod(client=admin_client, namespace=model_namespace.name) as minio_pod:
        yield minio_pod


@pytest.fixture(scope="class")
def minio_service(admin_client: DynamicClient, model_namespace: Namespace) -> Generator[MinioService]:
    with MinioService(client=admin_client, namespace=model_namespace.name) as minio_service:
        yield minio_service


@pytest.fixture(scope="class")
def minio_secret(admin_client: DynamicClient, model_namespace: Namespace) -> Generator[MinioSecret]:
    with MinioSecret(client=admin_client, namespace=model_namespace.name) as minio_secret:
        yield minio_secret


@pytest.fixture(scope="class")
def minio_data_connection(
    minio_service: MinioService, minio_pod: MinioPod, minio_secret: MinioSecret
) -> Generator[MinioSecret]:
    yield minio_secret
