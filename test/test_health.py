"""Provides tests for the 'get_health' endpoint functionality.

This module includes tests verifying status code, content type, and the JSON
structure of the endpoint's response.
"""

import pytest
from functions_framework import create_app

@pytest.mark.parametrize("source", ["get_health"], indirect=True)
class TestHealthEndpoint:
    """Get Health Endpoint Test."""

    def test_health_status_code(self, source):
        """Should return status code 200."""
        client = create_app("get_health", source).test_client()
        res = client.get("/")
        assert res.status_code == 200

    def test_health_content_type(self, source):
        """Should return response of content type json."""
        client = create_app("get_health", source).test_client()
        res = client.get("/")
        assert res.content_type == "application/json"

    def test_health_json_structure(self, source):
        """Should return healthy response json."""
        client = create_app("get_health", source).test_client()
        res = client.get("/")
        data = res.get_json()
        assert "healthy" in data
        assert data["healthy"] is True

    def test_health_json_structure_with_param(self, source):
        """Should return healthy response json with provided message."""
        test_message = "unitTestMessage"
        client = create_app("get_health", source).test_client()
        res = client.get(f"/?message={test_message}")
        data = res.get_json()
        assert "healthy" in data
        assert data["healthy"] is True
        assert "message" in data
        assert data["message"] == test_message

    def test_health_json_structure_with_wrong_param(self, source):
        """Should return error response json with wrong parameter provided."""
        
        test_parameter_name = "unitTestParameter"
        test_parameter_value = "unitTestValue"
        client = create_app("get_health", source).test_client()
        res = client.get(f"/?{test_parameter_name}={test_parameter_value}")
        data = res.get_json()
        assert "code" in data
        assert data["code"] == 400
        assert "message" in data
        assert data["message"] == "Invalid parameter provided."
