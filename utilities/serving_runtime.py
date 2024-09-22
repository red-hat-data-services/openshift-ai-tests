from typing import Any, Dict, List, Optional

from ocp_resources.serving_runtime import ServingRuntime


class ServingRuntimeForTests(ServingRuntime):
    def __init__(
        self,
        containers: List[Dict[str, str]],
        multi_model: bool = True,
        supported_model_formats: Optional[List[Dict[str, str]]] = None,
        built_in_adapter: Optional[Dict[str, Any]] = None,
        protocol_versions: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.containers = containers
        self.supported_model_formats = supported_model_formats
        self.multi_model = multi_model
        self.built_in_adapter = built_in_adapter
        self.protocol_versions = protocol_versions

        super().__init__(
            containers=self.containers,
            built_in_adapter=self.built_in_adapter,
            supported_model_formats=self.supported_model_formats,
            protocol_versions=self.protocol_versions,
            multi_model=self.multi_model,
            **kwargs,
        )
