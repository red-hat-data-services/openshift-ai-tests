global config

no_unprivileged_client = False
product = "RHODS"
operator_name = "rhods-operator"
applications_namespace = "redhat-ods-applications"
monitoring_namespace = "redhat-ods-monitoring"
operator_namespace = "redhat-ods-operator"
notebooks_namespace = "rhods-notebooks"

for _dir in dir():
    val = locals()[_dir]
    if type(val) not in [bool, list, dict, str, int]:
        continue

    if _dir in ["encoding", "py_file"]:
        continue

    config[_dir] = locals()[_dir]  # noqa: F821
