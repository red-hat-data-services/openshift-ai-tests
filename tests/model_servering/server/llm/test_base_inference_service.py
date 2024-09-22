import json
from urllib.parse import urlparse

import pytest

from tests.model_servering.server.llm.utils import run_grpc_command

pytestmark = pytest.mark.usefixtures("valid_aws_config")


@pytest.mark.parametrize(
    "model_namespace, storage_uri, llm_custom_isvc",
    [
        pytest.param(
            {"name": "flan-t5-small-caikit"},
            {"model-dir": "flan-t5-small/flan-t5-small-caikit"},
            {"deployment-mode": "Serverless"},
        )
    ],
    indirect=True,
)
class TestCustomInferenceService:
    def test_base_isvc_with_custom_class(self, llm_custom_isvc):
        assert llm_custom_isvc.exists


@pytest.mark.parametrize(
    "model_namespace, storage_uri, serving_runtime, inference_service",
    [
        pytest.param(
            {"name": "singlemodel-cli"},
            {"model-dir": "flan-t5-small/flan-t5-small-caikit"},
            {
                "name": "caikit-tgis-runtime",
                "model-name": "caikit",
                "multi-model": False,
            },
            {"name": "flan-t5-small-caikit"},
        )
    ],
    indirect=True,
)
class TestBaseInferenceService:
    def test_base_isvc_base_class(self, inference_service):
        inference_service.wait_for_condition(
            condition=inference_service.Condition.READY,
            status=inference_service.Condition.Status.TRUE,
            timeout=10 * 60,
        )

    def test_query_isvc(self, inference_service):
        query = {"text": "At what temperature does liquid Nitrogen boil?"}
        res = json.loads(
            run_grpc_command(
                url=urlparse(inference_service.instance.status.components.predictor.url).netloc,
                query=query,
            )
        )

        assert res["generated_text"] == "74 degrees F"
