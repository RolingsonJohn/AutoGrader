"""
Test fixtures and configuration for pytest.
"""

from services.Config.settings import Settings
from main import app
import pytest
import asyncio
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def settings():
    """Get test settings."""
    return Settings(
        fastapi_debug=True,
        fastapi_port=8001,
        api_key_groq="test-key",
        api_key_google="test-key"
    )


@pytest.fixture
def sample_evaluate_data():
    """Sample evaluation request data."""
    return {
        "task_id": 1,
        "theme": "python_basics",
        "prog_lang": "python",
        "model": "ollama",
        "agent": "test-agent",
        "api_key": "test-key",
        "authorization": "Bearer test-token"
    }


@pytest.fixture
def sample_populate_data():
    """Sample RAG populate request data."""
    return {
        "theme": "python_basics",
        "examples": [
            {"id": 1, "code": "print('Hello')"},
            {"id": 2, "code": "x = [1, 2, 3]"}
        ]
    }
