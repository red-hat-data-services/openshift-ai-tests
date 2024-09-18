# openshift-ai-tests
This is a framework to test [Red Hat OpenShift AI](https://www.redhat.com/en/technologies/cloud-computing/openshift/openshift-ai)
and its upstream project, [Open Data Hub](https://opendatahub.io/).


## Setup VirtualEnv
[Poetry](https://python-poetry.org/docs/) is used to manage virtualenv.
After installation, run:

```bash
poetry install
```

## How to run tests

### Run all tests

```bash
poetry run pytest
```

### Run a single test

```bash
poetry run pytest -k test_name
```

### Custom global_config to override the matrix value

To override the matrix value, you can create your own `global_config` file and pass the necessary parameters.

Example for AWS cluster:

`--tc-file=tests/global_config.py --product=ODH`


### Setting log level in command line

In order to run a test with a log level that is different from the default,
use the --log-cli-level command line switch.
The full list of possible log level strings can be found here:
https://docs.python.org/3/library/logging.html#logging-levels

When the switch is not used, we set the default level to INFO.

Example:
```bash
--log-cli-level=DEBUG
````
