import pytest


@pytest.mark.parametrize("isvc_ns", [pytest.param({"name": "test-ns"})], indirect=True)
def test_base_isvc(base_isvc):
    assert base_isvc.exists
