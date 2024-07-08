"""e2e test cases for testing the transform endpoint of the application."""

import requests
import unittest
import os
import logging
from xml.dom import minidom

class TestE2EPostTransform(unittest.TestCase):
    """A e2e test class for testing the transform endpoint of the application."""

    # Grundlegende Konfiguration des Loggings
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    REQUEST_TIMEOUT = 50


    def __normalize_xml( self, xml:str )->minidom.Document:
        return minidom.parseString( xml )


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

    def test_pnml_to_bpmn(self):
        """Tests the status code of the transform endpoint."""
        expected_response = {
            "bpmn": (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<bpmn:definitions xmlns:bpmn=\"http://www.omg.org/spec/BPMN/20100524"
                "/MODEL\" "
                "xmlns:bpmndi=\"http://www.omg.org/spec/BPMN/20100524/DI\" "
                "xmlns:dc=\"http://www.omg.org/spec/DD/20100524/DC\" "
                "xmlns:di=\"http://www.omg.org/spec/DD/20100524/DI\">"
                "<bpmn:process id=\"Process_05gf0wk\" isExecutable=\"true\">"
                "<bpmn:startEvent id=\"StartEvent_1kldrri\">"
                "<bpmn:outgoing>StartEvent_1kldrriTOActivity_16g2nsl</bpmn:outgoing>"
                "</bpmn:startEvent>"
                "<bpmn:endEvent id=\"Event_02tt0ub\">"
                "<bpmn:incoming>Activity_16g2nslTOEvent_02tt0ub</bpmn:incoming>"
                "</bpmn:endEvent>"
                "<bpmn:task id=\"Activity_16g2nsl\" name=\"Task\">"
                "<bpmn:incoming>StartEvent_1kldrriTOActivity_16g2nsl</bpmn:incoming>"
                "<bpmn:outgoing>Activity_16g2nslTOEvent_02tt0ub</bpmn:outgoing>"
                "</bpmn:task>"
                "<bpmn:sequenceFlow id=\"StartEvent_1kldrriTOActivity_16g2nsl\" source"
                "Ref=\"StartEvent_1kldrri\" targetRef=\"Activity_16g2nsl\" />"
                "<bpmn:sequenceFlow id=\"Activity_16g2nslTOEvent_02tt0ub\" source"
                "Ref=\"Activity_16g2nsl\" targetRef=\"Event_02tt0ub\" />"
                "</bpmn:process>"
                "<bpmndi:BPMNDiagram id=\"diagram1\">"
                "<bpmndi:BPMNPlane id=\"planeProcess_05gf0wk\" bpmnElement=\"Process_0"
                "5gf0wk\">"
                "<bpmndi:BPMNEdge id=\"StartEvent_1kldrriTOActivity_16g2nsl_di\" bpmn"
                "Element=\"StartEvent_1kldrriTOActivity_16g2nsl\">"
                "<di:waypoint x=\"0.0\" y=\"0.0\" /><di:waypoint x=\"0.0\" y=\"0.0\" />"
                "</bpmndi:BPMNEdge>"
                "<bpmndi:BPMNEdge id=\"Activity_16g2nslTOEvent_02tt0ub_di\" bpmn"
                "Element=\"Activity_16g2nslTOEvent_02tt0ub\">"
                "<di:waypoint x=\"0.0\" y=\"0.0\" /><di:waypoint x=\"0.0\" y=\"0.0\" />"
                "</bpmndi:BPMNEdge>"
                "<bpmndi:BPMNShape id=\"Activity_16g2nsl_di\" bpmn"
                "Element=\"Activity_16g2nsl\">"
                "<dc:Bounds x=\"0.0\" y=\"0.0\" width=\"100.0\" height=\"80.0\" />"
                "</bpmndi:BPMNShape>"
                "<bpmndi:BPMNShape id=\"StartEvent_1kldrri_di\" bpmnElement=\"Start"
                "Event_1kldrri\">"
                "<dc:Bounds x=\"0.0\" y=\"0.0\" width=\"100.0\" height=\"80.0\" />"
                "</bpmndi:BPMNShape>"
                "<bpmndi:BPMNShape id=\"Event_02tt0ub_di\" bpmnElement=\"Event_02tt0ub\""
                "><dc:Bounds x=\"0.0\" y=\"0.0\" width=\"100.0\" height=\"80.0\" />"
                "</bpmndi:BPMNShape>"
                "</bpmndi:BPMNPlane>"
                "</bpmndi:BPMNDiagram>"
                "</bpmn:definitions>"
            )
        }
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
            headers=self.shared_haeaders,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        logging.info(response.json())
        logging.info(expected_response)


        # self.assertEqual(response.json(), expected_response)

        normalizedExpectedXML = self.__normalize_xml( expected_response )
        normalizedActualXML   = self.__normalize_xml( response.json() )