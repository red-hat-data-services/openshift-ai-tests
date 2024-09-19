import logging
import os
import pathlib
import shutil

import pytest
from ocp_resources.inference_service import InferenceService
from ocp_resources.namespace import Namespace
from ocp_resources.node_config_openshift_io import Node
from ocp_resources.service import Service
from ocp_resources.serving_runtime import ServingRuntime
from simple_logger.logger import get_logger

from utilities.pytest_utils import (
    separator,
)

LOGGER = logging.getLogger(__name__)
BASIC_LOGGER = logging.getLogger("basic")

RESOURCES_TO_COLLECT_INFO = [
    InferenceService,
    ServingRuntime,
    Service,
    Namespace,
    Node,
]


def pytest_report_teststatus(report, config):  # type: ignore
    test_name = report.head_line
    when = report.when
    call_str = "call"
    if report.passed:
        if when == call_str:
            BASIC_LOGGER.info(f"\nTEST: {test_name} STATUS: \033[0;32mPASSED\033[0m")

    elif report.skipped:
        BASIC_LOGGER.info(f"\nTEST: {test_name} STATUS: \033[1;33mSKIPPED\033[0m")

    elif report.failed:
        if when != call_str:
            BASIC_LOGGER.info(f"\nTEST: {test_name} [{when}] STATUS: \033[0;31mERROR\033[0m")
        else:
            BASIC_LOGGER.info(f"\nTEST: {test_name} STATUS: \033[0;31mFAILED\033[0m")


def pytest_fixture_setup(fixturedef, request):  # type: ignore
    LOGGER.info(f"Executing {fixturedef.scope} fixture: {fixturedef.argname}")


def pytest_runtest_setup(item):  # type: ignore
    """
    Use incremental
    """
    BASIC_LOGGER.info(f"\n{separator(symbol_='-', val=item.name)}")
    BASIC_LOGGER.info(f"{separator(symbol_='-', val='SETUP')}")
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)


def pytest_sessionstart(session):  # type: ignore
    tests_log_file = session.config.getoption("pytest_log_file")
    if os.path.exists(tests_log_file):
        pathlib.Path(tests_log_file).unlink()

    session.config.option.log_listener = get_logger(
        name=__name__,
        filename=tests_log_file,
        level=session.config.getoption("log_cli_level") or logging.INFO,
    )


def pytest_sessionfinish(session, exitstatus):  # type: ignore
    shutil.rmtree(path=session.config.option.basetemp, ignore_errors=True)

    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    reporter.summary_stats()
