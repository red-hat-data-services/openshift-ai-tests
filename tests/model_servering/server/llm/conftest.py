import pytest
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError
from ocp_resources.inference_service import InferenceService
from ocp_resources.namespace import Namespace
from ocp_resources.resource import ResourceEditor, get_client
from ocp_resources.secret import Secret
from ocp_resources.service_account import ServiceAccount
from ocp_resources.service_mesh_member_roll import ServiceMeshMemberRoll
from ocp_resources.serving_runtime import ServingRuntime
from pytest_testconfig import config as py_config

from tests.model_servering.server.llm.utils import base64_encode_str
from utilities.inference_service import InferenceServiceForTests


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
def patched_service_mesh_member_roll(admin_client: DynamicClient, model_namespace: Namespace) -> ServiceMeshMemberRoll:
    smmr = ServiceMeshMemberRoll(client=admin_client, namespace="istio-system", name="default")

    if not smmr.exists:
        raise NotFoundError("istio ServiceMeshMemberRoll does not exist")

    members = smmr.instance.spec.members

    if members:
        members.append(model_namespace.name)
    else:
        members = [model_namespace.name]

    with ResourceEditor(patches={smmr: {"spec": {"members": members}}}):
        yield smmr


@pytest.fixture(scope="class")
def storage_uri(request) -> str:
    return f"s3://{py_config['model_s3_bucket_name']}/{request.param['model-dir']}/"


@pytest.fixture(scope="class")
def llm_custom_isvc(
    request, admin_client: DynamicClient, model_namespace: Namespace, storage_uri: str
) -> InferenceServiceForTests:
    name = model_namespace.name
    with InferenceServiceForTests(
        client=admin_client,
        namespace=name,
        name=name,
        deployment_mode=request.param["deployment-mode"],
        predictor_service_account_name="models-bucket-sa",
        predictor_model_format_name="pytorch",
        predictor_storage_uri=storage_uri,
    ) as isvc:
        yield isvc


@pytest.fixture(scope="class")
def endpoint_s3_secret(
    admin_client: DynamicClient,
    model_namespace: Namespace,
    aws_access_key: str,
    aws_secret_access_key: str,
) -> Secret:
    data = {
        "AWS_ACCESS_KEY_ID": base64_encode_str(text=aws_access_key),
        "AWS_SECRET_ACCESS_KEY": base64_encode_str(text=aws_secret_access_key),
        "AWS_S3_BUCKET": base64_encode_str(text=py_config["model_s3_bucket_name"]),
        "AWS_S3_ENDPOINT": base64_encode_str(text=py_config["model_s3_endpoint"]),
    }
    name = model_namespace.name

    with Secret(
        client=admin_client,
        namespace=name,
        name=name,
        data_dict=data,
    ) as secret:
        yield secret


@pytest.fixture(scope="class")
def model_service_account(admin_client: DynamicClient, endpoint_s3_secret: Namespace) -> ServiceAccount:
    with ServiceAccount(
        client=admin_client,
        namespace=endpoint_s3_secret.namespace,
        name="models-bucket-sa",
        secrets=[{"name": endpoint_s3_secret.name}],
    ) as sa:
        yield sa


@pytest.fixture(scope="class")
def serving_runtime(
    request,
    admin_client: DynamicClient,
    patched_service_mesh_member_roll,
    model_namespace: Namespace,
) -> ServingRuntime:
    containers = [
        {
            "name": "kserve-container",
            "image": "quay.io/modh/text-generation-inference@sha256:792e1500548c293eae428cf079fce836e68fbf7d4f7a53b5958c5158a70edfbf",
            "command": ["text-generation-launcher"],
            "args": ["--model-name=/mnt/models/artifacts/"],
            "env": [{"name": "TRANSFORMERS_CACHE", "value": "/tmp/transformers_cache"}],
        },
        {
            "name": "transformer-container",
            "image": "quay.io/modh/caikit-tgis-serving@sha256:3a2477e143c494280a81e50c31adb54fc9f2fd0a84dde3b31cf9f6929fb2d1f9",
            "env": [
                {"name": "RUNTIME_LOCAL_MODELS_DIR", "value": "/mnt/models"},
                {"name": "TRANSFORMERS_CACHE", "value": "/tmp/transformers_cache"},
                {"name": "RUNTIME_GRPC_ENABLED", "value": "true"},
                {"name": "RUNTIME_HTTP_ENABLED", "value": "false"},
            ],
            "ports": [{"containerPort": 8085, "name": "h2c", "protocol": "TCP"}],
        },
    ]

    with ServingRuntime(
        client=admin_client,
        name=request.param["name"],
        namespace=model_namespace.name,
        containers=containers,
        supported_model_formats=[
            {"name": request.param["model-name"], "autoselect": "true"},
        ],
        multi_model=request.param["multi-model"],
    ) as mlserver:
        yield mlserver


@pytest.fixture(scope="class")
def inference_service(
    request,
    admin_client: DynamicClient,
    model_namespace: Namespace,
    serving_runtime: ServingRuntime,
    endpoint_s3_secret: Secret,
    storage_uri: str,
    model_service_account: ServiceAccount,
) -> InferenceService:
    with InferenceService(
        client=admin_client,
        name=request.param["name"],
        namespace=model_namespace.name,
        annotations={
            "serving.knative.openshift.io/enablePassthrough": "true",
            "sidecar.istio.io/inject": "true",
            "sidecar.istio.io/rewriteAppHTTPProbers": "true",
        },
        predictor={
            "model": {
                "modelFormat": {"name": serving_runtime.instance.spec.supportedModelFormats[0].name},
                "runtime": serving_runtime.name,
                "storageUri": storage_uri,
            },
            "serviceAccountName": model_service_account.name,
        },
    ) as inference_service:
        yield inference_service
