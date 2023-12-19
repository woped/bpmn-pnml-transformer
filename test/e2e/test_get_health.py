

import requests
import unittest

import os

class TestE2EGetHealth(unittest.TestCase):
    """A e2e test class for testing the health endpoint of the application."""
    
    REQUEST_TIMEOUT = 50

    def setUp(self):
        """Performs setup before each test case."""
        self.url = os.getenv("E2E_URL")
    
    def test_status_code(self):
        """Tests the status code of the health endpoint."""
        response = requests.get(self.url, timeout=self.REQUEST_TIMEOUT)
        self.assertEqual(response.status_code, 200)
    
    def test_content_type(self):
        """Tests the content type of the health endpoint."""
        response = requests.get(self.url, timeout=self.REQUEST_TIMEOUT)
        self.assertEqual(response.headers["Content-Type"], "application/json")

    def test_res_body(self):
        """Tests the response body of the health endpoint."""
        response = requests.get(self.url, timeout=self.REQUEST_TIMEOUT)
        self.assertEqual(response.json(), {"healthy": True})
    
    def test_res_body_with_param(self):
        """Tests the response body of the health endpoint with a provided parameter."""
        message = "e2eTestMessage"
        response = requests.get(f'{self.url}?message={message}', timeout=self.REQUEST_TIMEOUT)
        self.assertEqual(response.json(), {"healthy": True, "message": message})
    
    def test_res_body_with_unkown_param(self):
        """Tests the response body of the health endpoint with an unknown parameter."""
        message = "e2eTestMessage"
        response = requests.get(f'{self.url}?unkownParameter={message}', timeout=self.REQUEST_TIMEOUT)
        expected_res_body = {"code": 400, "message": "Invalid parameter provided."} 
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_res_body)