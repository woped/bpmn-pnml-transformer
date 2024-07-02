"""e2e test cases for testing the transform endpoint of the application."""

import requests
import unittest
import os

class TestE2EPostTransform(unittest.TestCase):
    """A e2e test class for testing the transform endpoint of the application."""

    REQUEST_TIMEOUT = 50

    def setUp(self):
        """Performs setup before each test case."""
        self.url = os.getenv("E2E_URL")
        if self.url is None:
            raise ValueError("E2E_URL environment variable not set.")
        self.token = os.getenv("E2E_IDENTITY_TOKEN")
        if self.token is None:
            raise ValueError("E2E_IDENTITY_TOKEN environment variable not set.")
        self.shared_haeaders = {
            "Authorization": f"Bearer {self.token}"
        }

    def test_pnml_to_bpmn(self):
        """Tests the transform endpoint for direction pnmltobpmn."""
        pnml_xml_path = "../../diagrams/xml/e2e_pnml_req"
        with open(pnml_xml_path, encoding='utf-8') as file:
            pnml_string = file.read()
        bpmn_xml = '../../diagrams/xml/e2e_bpmn_res.xml'
        with open(bpmn_xml, encoding='utf-8') as file:
            bpmn_string = file.read()
        expected_response = {
            "bpmn": bpmn_string
        }
        payload = {
            "pnml": pnml_string
        }
        response = requests.post(
            f'{self.url}?direction=pnmltobpmn', 
            data = payload,
            timeout=self.REQUEST_TIMEOUT,
            headers=self.shared_haeaders,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.json(), expected_response)

    def test_bpmn_to_pnml(self):
        """Tests the transform endpoint for direction bpmntopnml."""
        expected_response = {
            "pnml": (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?><pnml id=\"\">"
                "<net id=\"Process_05gf0wk\"><place id=\"StartEvent_1kldrri\" />"
                "<place id=\"Event_02tt0ub\" /><transition id=\"Activity_16g2nsl\">"
                "<name id=\"\"><graphics id=\"\"><offset id=\"\" x=\"20.0\" "
                "y=\"20.0\" /></graphics><text>Task</text></name></transition>"
                "<arc id=\"Activity_16g2nslTOEvent_02tt0ub\" "
                "source=\"Activity_16g2nsl\" target=\"Event_02tt0ub\" />"
                "<arc id=\"StartEvent_1kldrriTOActivity_16g2nsl\" "
                "source=\"StartEvent_1kldrri\" target=\"Activity_16g2nsl\" />"
                "</net></pnml>"
            )
        }
        payload = {
            "bpmn": (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?> "
                "<bpmn:definitions xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance"
                "\" xmlns:bpmn=\"http://www.omg.org/spec/BPMN/20100524/MODEL\" "
                "xmlns:bpmndi=\"http://www.omg.org/spec/BPMN/20100524/DI\" "
                "xmlns:dc=\"http://www.omg.org/spec/DD/20100524/DC\" "
                "xmlns:di=\"http://www.omg.org/spec/DD/20100524/DI\" "
                "id=\"Definitions_0uh33yr\" targetNamespace=\"http://bpmn.io/schema/"
                "bpmn\" exporter=\"bpmn-js (https://demo.bpmn.io)\" exporterVersion"
                "=\"17.6.2\"><bpmn:process id=\"Process_05gf0wk\" isExecutable=\"false"
                "\"><bpmn:startEvent id=\"StartEvent_1kldrri\">"
                "<bpmn:outgoing>Flow_03wmhzd</bpmn:outgoing></bpmn:startEvent>"
                "<bpmn:task id=\"Activity_16g2nsl\" name=\"Task\">"
                "<bpmn:incoming>Flow_03wmhzd</bpmn:incoming><bpmn:outgoing>Flow_06lknmg"
                "</bpmn:outgoing></bpmn:task><bpmn:sequenceFlow id=\"Flow_03wmhzd\" "
                "sourceRef=\"StartEvent_1kldrri\" targetRef=\"Activity_16g2nsl\" />"
                "<bpmn:endEvent id=\"Event_02tt0ub\"><bpmn:incoming>Flow_06lknmg"
                "</bpmn:incoming></bpmn:endEvent><bpmn:sequenceFlow id=\"Flow_06lknmg\" "
                "sourceRef=\"Activity_16g2nsl\" targetRef=\"Event_02tt0ub\" />"
                "</bpmn:process><bpmndi:BPMNDiagram id=\"BPMNDiagram_1\">"
                "<bpmndi:BPMNPlane id=\"BPMNPlane_1\" bpmnElement=\"Process_03gf0wk\">"
                "<bpmndi:BPMNShape id=\"_BPMNShape_StartEvent_2\" bpmnElement"
                "=\"StartEvent_1kldrri\"><dc:Bounds x=\"156\" y=\"82\" width=\"36\" "
                "height=\"36\" /></bpmndi:BPMNShape><bpmndi:BPMNShape "
                "id=\"Activity_16g2nsl_di\" bpmnElement=\"Activity_16g2nsl\"><dc:Bounds "
                "x=\"250\" y=\"60\" width=\"100\" height=\"80\" /><bpmndi:BPMNLabel />"
                "</bpmndi:BPMNShape><bpmndi:BPMNShape id=\"Event_02tt0ub_di\" "
                "bpmnElement=\"Event_02tt0ub\"><dc:Bounds x=\"412\" y=\"82\" "
                "width=\"36\" height=\"36\" /></bpmndi:BPMNShape><bpmndi:BPMNEdge "
                "id=\"Flow_03wmhzd_di\" bpmnElement=\"Flow_03wmhzd\">"
                "<di:waypoint x=\"192\" y=\"100\" /><di:waypoint x=\"250\" y=\"100\" />"
                "</bpmndi:BPMNEdge><bpmndi:BPMNEdge id=\"Flow_06lknmg_di\" "
                "bpmnElement=\"Flow_06lknmg\"><di:waypoint x=\"350\" y=\"100\" />"
                "<di:waypoint x=\"412\" y=\"100\" /></bpmndi:BPMNEdge>"
                "</bpmndi:BPMNPlane></bpmndi:BPMNDiagram></bpmn:definitions>"
            )
        }
        response = requests.post(
            f'{self.url}?direction=bpmntopnml', 
            data = payload,
            timeout=self.REQUEST_TIMEOUT,
            headers=self.shared_haeaders,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.json(), expected_response)
