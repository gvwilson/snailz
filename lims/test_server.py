"""Test LIMS server."""

import pytest

from app import app


@pytest.fixture
def client(data):
    app.config["data"] = data
    app.config["memory"] = True
    return app.test_client()


def test_load_home_page(client, data):
    res = client.get("/")
    assert res.status_code == 200
    assert "LIMS" in res.get_data(as_text=True)
