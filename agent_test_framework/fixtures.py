import pytest
import os
import yaml
from agent_test_framework.utils.test_hooks import run_hook

GLOBAL_HOOKS_FILE = os.path.join("config", "global_hooks.yaml")

def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Environment to run tests against (dev, stage, prod)",
    )

def pytest_configure(config):
    config.env = config.getoption("env")

@pytest.fixture(scope="session")
def test_env(pytestconfig):
    return pytestconfig.getoption("env")

@pytest.fixture(scope="session", autouse=True)
def global_session_fixture():
    if not os.path.exists(GLOBAL_HOOKS_FILE):
        print("[Global Hooks] Skipping: config/global_hooks.yaml not found.")
        yield
        return

    with open(GLOBAL_HOOKS_FILE) as f:
        hooks = yaml.safe_load(f)

    setup_hook = hooks.get("setup")
    teardown_hook = hooks.get("teardown")

    run_hook(setup_hook, stage="GLOBAL_SESSION_SETUP")
    yield
    run_hook(teardown_hook, stage="GLOBAL_SESSION_TEARDOWN")
