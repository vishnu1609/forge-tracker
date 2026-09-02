"""
Shared pytest fixtures for FORGE unit tests.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client with chainable query methods."""
    mock = MagicMock()

    # Make chained calls return the mock itself for fluent API
    mock.table.return_value = mock
    mock.select.return_value = mock
    mock.insert.return_value = mock
    mock.delete.return_value = mock
    mock.update.return_value = mock
    mock.eq.return_value = mock
    mock.neq.return_value = mock
    mock.order.return_value = mock
    mock.limit.return_value = mock

    return mock


@pytest.fixture
def app(mock_supabase):
    """Create a Flask test app with mocked Supabase."""
    with patch.dict('os.environ', {
        'SUPABASE_URL': 'https://fake.supabase.co',
        'SUPABASE_KEY': 'fake-key',
        'FLASK_SECRET_KEY': 'test-secret',
    }):
        with patch('app.supabase', mock_supabase):
            from app import app as flask_app
            flask_app.config['TESTING'] = True
            yield flask_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()
