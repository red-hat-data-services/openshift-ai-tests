from typing import Any, Dict, List, Optional

from ocp_resources.inference_service import InferenceService


class InferenceServiceForTests(InferenceService):
    def __init__(
        self,
        deployment_mode: str = "RawDeployment",
        dashboard: bool = True,
        predictor_min_replicas: Optional[int] = None,
        predictor_max_replicas: Optional[int] = None,
        predictor_service_account_name: Optional[str] = None,
        predictor_model_format_name: Optional[str] = None,
        predictor_runtime: Optional[str] = None,
        predictor_storage_uri: Optional[str] = None,
        predictor_model_args: Optional[List[str]] = None,
        predictor_env_variables: Optional[Dict[str, str]] = None,
        predictor_gpu_resources: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        self.deployment_mode = deployment_mode
        self.dashboard = dashboard
        self.predictor_service_account_name = predictor_service_account_name
        self.predictor_min_replica = predictor_min_replicas
        self.predictor_max_replica = predictor_max_replicas
        self.predictor_model_format_name = predictor_model_format_name
        self.predictor_runtime_name = predictor_runtime
        self.predictor_storage_uri = predictor_storage_uri
        self.predictor_model_arg = predictor_model_args
        self.predictor_env_variables = predictor_env_variables
        self.predictor_gpu_resources = predictor_gpu_resources

        self.annotations = self.set_annotations()
        self.predictor = self.prepare_predictor()

        super().__init__(
            annotations=self.annotations,
            predictor=self.predictor,
            **kwargs,
        )

    def prepare_predictor(self) -> Dict[str, Any]:
        _predictor: Dict[str, Any] = {"model": {}}
        _predictor_model = _predictor["model"]

        if self.predictor_service_account_name:
            _predictor.setdefault("serviceAccountName", self.predictor_service_account_name)

        if self.predictor_min_replica:
            _predictor.setdefault("minReplicas", self.predictor_min_replica)

        if self.predictor_max_replica:
            _predictor.setdefault("maxReplicas", self.predictor_max_replica)

        if self.predictor_gpu_resources:
            _predictor = self.set_predictor_gpu_config(predictor_spec=_predictor)

        if self.predictor_model_format_name:
            _predictor_model.setdefault("modelFormat", {"name": self.predictor_model_format_name})

        if self.predictor_runtime_name:
            _predictor_model["runtime"] = self.predictor_runtime_name

        if self.predictor_storage_uri:
            _predictor_model["storageUri"] = self.predictor_storage_uri

        if self.predictor_env_variables:
            _predictor_model = self.set_predictor_env_variables(predictor_model_spec=_predictor_model)

        if self.predictor_model_arg:
            _predictor_model = self.set_predictor_model_arg(predictor_model_spec=_predictor_model)

        return _predictor

    def set_annotations(self) -> Dict[str, str]:
        annotations: Dict[str, str] = {"serving.kserve.io/deploymentMode": self.deployment_mode}

        if self.dashboard:
            annotations["serving.kserve.io/dashboards"] = "true"

        return annotations

    def set_predictor_env_variables(self, predictor_model_spec: Dict[str, Any]) -> Dict[str, Any]:
        env_vars: List[Dict[str, str]] = [{"name": "HF_HUB_CACHE", "value": "/tmp"}]

        for name, value in self.predictor_env_variables.items():  # type: ignore
            env_vars.append({"name": name, "value": value})

        predictor_model_spec["env"] = env_vars

        return predictor_model_spec

    def set_predictor_gpu_config(self, predictor_spec: Dict[str, Any]) -> Dict[str, Any]:
        predictor_spec = self.set_predictor_gpu_resource(predictor_spec=predictor_spec)

        predictor_spec = self.set_predictor_volumes_and_volume_mounts(predictor_spec=predictor_spec)

        return predictor_spec

    def set_predictor_gpu_resource(self, predictor_spec: Dict[str, Any]) -> Dict[str, Any]:
        spec = predictor_spec["spec"]
        spec.setdefault("resources", {}).setdefault("requests", {})
        spec["resources"]["requests"].update({
            self.predictor_gpu_resources["gpu_locator"]: self.predictor_gpu_resources["gpu_count"]  # type: ignore
        })

        return predictor_spec

    def set_predictor_volumes_and_volume_mounts(self, predictor_spec: Dict[str, Any]) -> Dict[str, Any]:
        if self.predictor_gpu_resources["gpu_count"] > "1":  # type: ignore
            spec = predictor_spec["spec"]
            spec.setdefault("volumeMounts", []).extend([
                {
                    "name": "gshared-memory",
                    "mountPath": "/dev/shm",
                },
                {
                    "name": "tmp",
                    "mountPath": "//tmp",
                },
                {
                    "name": "home",
                    "mountPath": "/home/vllm",
                },
            ])

            spec.setdefault("volumes", []).append(
                {
                    "name": "gshared-memory",
                    "emptyDir": {"medium": "Memory", "sizeLimit": "16Gi"},
                },
            )

        return predictor_spec

    def set_predictor_model_arg(self, predictor_model_spec: Dict[str, Any]) -> Dict[str, Any]:
        spec = predictor_model_spec

        for arg in self.predictor_model_arg:  # type: ignore
            spec.setdefault("args", []).append(arg)

        return predictor_model_spec
