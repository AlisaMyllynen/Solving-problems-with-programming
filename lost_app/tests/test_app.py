import os
import tempfile

import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    db_file = tmp_path / "test.db"
    app = create_app({'TESTING': True, 'DATABASE': str(db_file)})

    with app.test_client() as client:
        with app.app_context():
            app.init_db()
        yield client


def test_index_empty(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'No items reported yet' in resp.data


def test_report_item(client):
    resp = client.post('/report', data={'title': 'Wallet', 'description': 'Black leather', 'location': 'Cafe', 'date_lost': '2025-10-07', 'contact': 'me@example.com'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Wallet' in resp.data
