"""Pytest configuration file."""
import pytest

# Set default pytest-asyncio mode to strict
pytest.ini_options = {
    "asyncio_mode": "strict",
    "asyncio_default_fixture_loop_scope": "function"
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close() 