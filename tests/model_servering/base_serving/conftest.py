import pytest
from jedi.inference.value.iterable import Generator
from kubernetes.dynamic import DynamicClient
from ocp_resources.namespace import Namespace
from ocp_resources.resource import get_client

from utilities.inference_service import InferenceServiceForTests


@pytest.fixture(scope="session")
def admin_client() -> DynamicClient:
    return get_client()


@pytest.fixture
def isvc_ns(request, admin_client: DynamicClient):  # type: ignore
    with Namespace(
        client=admin_client,
        name=request.param["name"],
    ) as ns:
        ns.wait_for_status(status=Namespace.Status.ACTIVE, timeout=120)
        yield ns


@pytest.fixture
def base_isvc(admin_client: DynamicClient, isvc_ns: Namespace) -> Generator:
    with InferenceServiceForTests(
        client=admin_client,
        namespace=isvc_ns.name,
        name="sklearn-iris",
        deployment_mode="Serverless",
        predictor_service_account_name="seldon",
        predictor_model_format_name="pytorch",
        predictor_storage_uri="s3://ods-ci-wisdom/ELYZA-japanese-Llama-2-7b-instruct-hf/",
        predictor_runtime="vllm-runtime",
        predictor_model_args=["--dtype=bfloat16"],
    ) as isvc:
        yield isvc
