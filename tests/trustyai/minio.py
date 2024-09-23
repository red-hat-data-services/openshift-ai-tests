from typing import Any

from ocp_resources.pod import Pod
from ocp_resources.secret import Secret
from ocp_resources.service import Service


MINIO: str = "minio"
OPENDATAHUB_IO: str = "opendatahub.io"
MINIO_DATA_CONNECTION_NAME: str = "aws-connection-minio-data-connection"


class MinioPod(Pod):
    def __init__(self, namespace: str, **kwargs: Any) -> None:
        super().__init__(
            name=MINIO,
            namespace=namespace,
            containers=[
                {
                    "args": [
                        "server",
                        "/data1",
                    ],
                    "env": [
                        {
                            "name": "MINIO_ACCESS_KEY",
                            "value": "THEACCESSKEY",
                        },
                        {
                            "name": "MINIO_SECRET_KEY",
                            "value": "THESECRETKEY",
                        },
                    ],
                    "image": "quay.io/trustyai/modelmesh-minio-examples@"
                    "sha256:e8360ec33837b347c76d2ea45cd4fea0b40209f77520181b15e534b101b1f323",
                    "name": MINIO,
                }
            ],
            label={"app": "minio", "maistra.io/expose-route": "true"},
            annotations={"sidecar.istio.io/inject": "true"},
            **kwargs,
        )


class MinioService(Service):
    def __init__(self, namespace: str, **kwargs: Any) -> None:
        super().__init__(
            name="minio",
            namespace=namespace,
            ports=[
                {
                    "name": "minio-client-port",
                    "port": 9000,
                    "protocol": "TCP",
                    "targetPort": 9000,
                }
            ],
            selector={
                "app": "minio",
            },
        )


class MinioSecret(Secret):
    def __init__(self, namespace: str, **kwargs: Any) -> None:
        super().__init__(
            name="aws-connection-minio-data-connection",
            namespace=namespace,
            data_dict={
                "AWS_ACCESS_KEY_ID": "VEhFQUNDRVNTS0VZ",
                "AWS_DEFAULT_REGION": "dXMtc291dGg=",
                "AWS_S3_BUCKET": "bW9kZWxtZXNoLWV4YW1wbGUtbW9kZWxz",
                "AWS_S3_ENDPOINT": "aHR0cDovL21pbmlvOjkwMDA=",
                "AWS_SECRET_ACCESS_KEY": "VEhFU0VDUkVUS0VZ",
            },
            label={
                f"{OPENDATAHUB_IO}/dashboard": "true",
                f"{OPENDATAHUB_IO}/managed": "true",
            },
            annotations={
                f"{OPENDATAHUB_IO}/connection-type": "s3",
                "openshift.io/display-name": "Minio Data Connection",
            },
        )
