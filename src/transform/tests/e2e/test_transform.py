"""e2e test cases for testing the transform endpoint of the application."""

from xxlimited import Str
import requests
import unittest
import logging
from xml.dom import minidom
import os

class TestE2EPostTransform(unittest.TestCase):
    """A e2e test class for testing the transform endpoint of the application."""

    # Grundlegende Konfiguration des Loggings
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    REQUEST_TIMEOUT = 50


    def __normalize_xml( self, xml_string:str )->Str():
        return minidom.parseString( xml_string)\
            .toxml()\
            .replace( "\n", "" )\
            .replace( "\t", "" )\
            .replace( "\r", "" )


    def setUp(self):
        """Performs setup before each test case."""
        self.url = os.getenv("E2E_URL")
        self.maxDiff = None
        if self.url is None:
            raise ValueError("E2E_URL environment variable not set.")
        self.token = os.getenv("E2E_IDENTITY_TOKEN")
        if self.token is None:
            raise ValueError("E2E_IDENTITY_TOKEN environment variable not set.")
        self.shared_haeaders = {
            "Authorization": f"Bearer {self.token}"
        }
        # self.maxDiff = None
        # self.url = "https://europe-west3-woped-422510.cloudfunctions.net/transform"

    def test_pnml_to_bpmn(self):
        """Tests the status code of the transform endpoint."""
        PAYLOAD_PNML_FILE_PATH =\
            'tests/assets/diagrams/pnml/e2e_payload.xml'
        with open( PAYLOAD_PNML_FILE_PATH, encoding='utf-8') as file:
            payload_content = file.read()

        EXPECTED_BPMN_FILE_PATH =\
            'tests/assets/diagrams/bpmn/e2e_expected_response.xml'
        with open( EXPECTED_BPMN_FILE_PATH, encoding='utf-8') as file:
            expected_response = file.read()

        payload = {"pnml": payload_content}

        response = requests.post(
            f'{self.url}?direction=pnmltobpmn', 
            data = payload,
            timeout=self.REQUEST_TIMEOUT,
            headers=self.shared_haeaders,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")

        normalized_expected_xml = self.__normalize_xml( expected_response       )
        normalized_actual_xml   = self.__normalize_xml( response.json()["bpmn"] )

        self.assertEqual( normalized_expected_xml, normalized_actual_xml )
