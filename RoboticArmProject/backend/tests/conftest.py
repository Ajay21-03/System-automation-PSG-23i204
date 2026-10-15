"""pytest fixtures shared across backend tests."""
import os
import sys
import pytest

# Make sure app package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.services.persistence import init_db


@pytest.fixture(scope="session")
def app():
    test_app = create_app({"TESTING": True})
    with test_app.app_context():
        init_db()
        yield test_app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
