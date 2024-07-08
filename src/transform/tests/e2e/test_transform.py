"""e2e test cases for testing the transform endpoint of the application."""

from xxlimited import Str
import requests
import unittest
import logging
from xml.dom import minidom

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
        # self.url = os.getenv("E2E_URL")
        # self.maxDiff = None
        # if self.url is None:
        #     raise ValueError("E2E_URL environment variable not set.")
        # self.token = os.getenv("E2E_IDENTITY_TOKEN")
        # if self.token is None:
        #     raise ValueError("E2E_IDENTITY_TOKEN environment variable not set.")
        # self.shared_haeaders = {
        #     "Authorization": f"Bearer {self.token}"
        # }
        self.maxDiff = None
        self.url = "https://europe-west3-woped-422510.cloudfunctions.net/transform"

    def test_pnml_to_bpmn(self):
        """Tests the status code of the transform endpoint."""
        EXPECTED_XML_FILE_PATH =\
            'tests/assets/diagrams/bpmn/expected_response.xml'
        with open( EXPECTED_XML_FILE_PATH, encoding='utf-8') as file:
            expected_response = file.read()

        payload = {
            "pnml": (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?><pnml><net id=\"Process_0"
                "5gf0wk\"><place id=\"StartEvent_1kldrri\" /><place id=\"Event_02t"
                "t0ub\" /><transition id=\"Activity_16g2nsl\"><name><graphics><offset x"
                "=\"20.0\" y=\"20.0\" /></graphics><text>Task</text></name></transition>"
                "<arc id=\"Activity_16g2nslTOEvent_02tt0ub\" source=\"Activity_16g2nsl\""
                " target=\"Event_02tt0ub\" /><arc id=\"StartEvent_1kldrriTOActivity_16"
                "g2nsl\" source=\"StartEvent_1kldrri\" target=\"Activity_16g2nsl\" />"
                "</net></pnml>"
            )
        }
        response = requests.post(
            f'{self.url}?direction=pnmltobpmn', 
            data = payload,
            timeout=self.REQUEST_TIMEOUT,
            # headers=self.shared_haeaders,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")

        normalized_expected_xml = self.__normalize_xml( expected_response       )
        normalized_actual_xml   = self.__normalize_xml( response.json()["bpmn"] )

        self.assertEqual( normalized_expected_xml, normalized_actual_xml )
