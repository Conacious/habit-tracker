import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_test_environment():
    os.environ["DATABASE_MODE"] = "inmemory"
