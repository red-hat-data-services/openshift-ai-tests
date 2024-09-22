import os

global config

no_unprivileged_client = False
product = "RHODS"
operator_name = "rhods-operator"
applications_namespace = "redhat-ods-applications"
monitoring_namespace = "redhat-ods-monitoring"
operator_namespace = "redhat-ods-operator"
notebooks_namespace = "rhods-notebooks"

aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "aws_secret_key")
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "aws_access_key")

model_s3_bucket_name = "s3-bucket"
model_s3_bucket_region = "us-east-1"
model_s3_endpoint = f"https://{model_s3_bucket_region}.amazonaws.com/"

for _dir in dir():
    val = locals()[_dir]
    if type(val) not in [bool, list, dict, str, int]:
        continue

    if _dir in ["encoding", "py_file"]:
        continue

    config[_dir] = locals()[_dir]  # noqa: F821
