"""Unit tests for the health endpoint of the application."""
import unittest
from functions_framework import create_app


class TestUnitGetHealth(unittest.TestCase):
    """A unit test class for testing the health endpoint of the application."""

    def setUp(self):
        """Performs setup before each test case."""
        self.client = create_app(
            "get_health",
            "main.py",
        ).test_client()

    def test_status_code(self):
        """Tests the status code of the health endpoint."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_content_type(self):
        """Tests the content type of the health endpoint."""
        response = self.client.get('/')
        self.assertEqual(response.content_type, 'application/json')

    def test_res_body(self):
        """Tests the response body of the health endpoint."""
        response = self.client.get('/')
        self.assertEqual(response.get_json(), {"healthy": True})

    def test_res_body_with_param(self):
        """Tests the response body of the health endpoint with a provided parameter."""
        message = "unitTestMessage"
        response = self.client.get(f'/?message={message}')
        self.assertEqual(response.get_json(), {"healthy": True, "message": message})

    def test_res_body_with_unkown_param(self):
        """Tests the response body of the health endpoint with an unknown parameter."""
        message = "unitTestMessage"
        response = self.client.get(f'/?unkownParameter={message}')
        expected_res_body = {"code": 400, "message": "Invalid parameter provided."} 
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), expected_res_body)
    
if __name__ == '__main__':
    unittest.main()
