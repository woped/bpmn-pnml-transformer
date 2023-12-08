import pytest
from functions_framework import create_app

@pytest.mark.parametrize("source", ["get_health"], indirect=True)
def test_health_status_code(source):
    client = create_app("get_health", source).test_client()
    res = client.get("/")
    assert res.status_code == 200

@pytest.mark.parametrize("source", ["get_health"], indirect=True)
def test_health_content_type(source):
    client = create_app("get_health", source).test_client()
    res = client.get("/")
    assert res.content_type == "application/json"

@pytest.mark.parametrize("source", ["get_health"], indirect=True)
def test_health_json_structure(source):
    client = create_app("get_health", source).test_client()
    res = client.get("/")
    data = res.get_json()
    assert "healthy" in data
    assert data["healthy"] is True

