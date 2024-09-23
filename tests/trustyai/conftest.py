from typing import Generator

import pytest
from ocp_resources.namespace import Namespace

from tests.trustyai.minio import MinioPod, MinioService, MinioSecret


@pytest.fixture(scope="class")
def minio_pod(model_namespace: Namespace) -> Generator[MinioPod]:
    with MinioPod(namespace=model_namespace.name) as minio_pod:
        yield minio_pod


@pytest.fixture(scope="class")
def minio_service(model_namespace: Namespace) -> Generator[MinioService]:
    with MinioService(namespace=model_namespace.name) as minio_service:
        yield minio_service


@pytest.fixture(scope="class")
def minio_secret(model_namespace: Namespace) -> Generator[MinioSecret]:
    with MinioSecret(namespace=model_namespace) as minio_secret:
        yield minio_secret


@pytest.fixture(scope="class")
def minio_data_connection(
    minio_service: MinioService, minio_pod: MinioPod, minio_secret: MinioSecret
) -> Generator[MinioSecret]:
    yield minio_secret
