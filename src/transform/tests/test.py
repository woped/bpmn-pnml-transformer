import shutil
import unittest
from pathlib import Path

from testgeneration.testcases.bpmn_to_pnml.ignored_cases import (
    all_cases as ignored_cases_bpmn,
)
from testgeneration.testcases.bpmn_to_pnml.supported_cases import (
    all_cases as supported_cases_bpmn,
)
from testgeneration.testcases.bpmn_to_pnml.supported_cases_workflow import (
    supported_cases_workflow_bpmn,
)
from testgeneration.testcases.bpmn_to_pnml.unsupported_cases import (
    all_cases as unsupported_cases_bpmn,
)
from testgeneration.testcases.pnml_to_bpmn.supported_cases import (
    all_cases as supported_cases_pnml,
)
from testgeneration.testcases.pnml_to_bpmn.supported_cases_workflow import (
    supported_cases_workflow_pnml,
)
from testgeneration.utility import clear

from transformer.equality.bpmn import compare_bpmn
from transformer.equality.petrinet import compare_pnml
from transformer.exceptions import NotSupportedBPMNElement
from transformer.models.bpmn.bpmn import BPMN
from transformer.models.pnml.pnml import Pnml
from transformer.transform_bpmn_to_petrinet.transform import (
    bpmn_to_st_net,
    bpmn_to_st_net_from_xml,
    bpmn_to_workflow_net,
)
from transformer.transform_petrinet_to_bpmn.transform import pnml_to_bpmn

LOG_PATH = "test_log"


def save_failed_bpmn_to_pnml_transformation(
    pn_expected: Pnml, pn_transformed: Pnml, bpmn: BPMN, case: str
):
    def create_path(file_name: str = ""):
        p = f"{LOG_PATH}/{case}/{file_name}"
        return p

    Path(create_path()).mkdir(parents=True, exist_ok=True)

    pn_expected.write_to_file(create_path("expected.pnml"))
    pn_transformed.write_to_file(create_path("transformed.pnml"))
    bpmn.write_to_file(create_path("source.bpmn"))

    bpmn.to_pm4py_vis(create_path("bpmn.png"))
    pn_expected.to_pm4py_vis(create_path("expected.png"))
    pn_transformed.to_pm4py_vis(create_path("transformed.png"))


def save_failed_pnml_to_bpmn_transformation(
    bpmn_expected: BPMN, bpmn_transformed: BPMN, net: Pnml, case: str
):
    def create_path(file_name: str = ""):
        return f"{LOG_PATH}/{case}/{file_name}"

    Path(create_path()).mkdir(parents=True, exist_ok=True)

    bpmn_expected.write_to_file(create_path("expected.bpmn"))
    bpmn_transformed.write_to_file(create_path("transformed.bpmn"))
    net.write_to_file(create_path("source.pnml"))

    bpmn_expected.to_pm4py_vis(create_path("expected.png"))
    bpmn_transformed.to_pm4py_vis(create_path("transformed.png"))
    net.to_pm4py_vis(create_path("source.png"))


class TestPetriNetToBPMN(unittest.TestCase):
    def test_supported_elements(self):
        for bpmn_expected, net, case in supported_cases_pnml:
            bpmn_transformed = pnml_to_bpmn(net)
            equal, error = compare_bpmn(bpmn_expected, bpmn_transformed)
            if not equal:
                save_failed_pnml_to_bpmn_transformation(
                    bpmn_expected, bpmn_transformed, net, case
                )
            with self.subTest(case):
                self.assertTrue(equal, f"{case} should be equal\n{error}")


class TestWorkflowNetToBPMN(unittest.TestCase):
    def test_supported_workflow_elements(self):
        for bpmn_expected, net, case in supported_cases_workflow_pnml:
            bpmn_transformed = pnml_to_bpmn(net)
            equal, error = compare_bpmn(bpmn_expected, bpmn_transformed)
            if not equal:
                save_failed_pnml_to_bpmn_transformation(
                    bpmn_expected, bpmn_transformed, net, case
                )
            with self.subTest(case):
                self.assertTrue(equal, f"{case} should be equal\n{error}")


class TestBPMNToPetriNet(unittest.TestCase):
    def test_supported_elements(self):
        for bpmn, pn_expected, case in supported_cases_bpmn:
            pn_transformed = bpmn_to_st_net(bpmn)
            equal, error = compare_pnml(pn_expected.net, pn_transformed.net)
            if not equal:
                save_failed_bpmn_to_pnml_transformation(
                    pn_expected, pn_transformed, bpmn, case
                )
            with self.subTest(case):
                self.assertTrue(equal, f"{case} should be equal\n{error}")

    def test_unsupported_elemnts(self):
        for bpmn_xml, name in unsupported_cases_bpmn:
            with self.assertRaises(NotSupportedBPMNElement):
                bpmn_to_st_net_from_xml(bpmn_xml)
        clear()

    def test_ignore_elements(self):
        for bpmn_xml, pn_truth in ignored_cases_bpmn:
            pn_transformed = bpmn_to_st_net_from_xml(bpmn_xml)
            equal, error = compare_pnml(pn_truth.net, pn_transformed.net)
            self.assertTrue(equal, f"should be equal\n{error}")
        clear()


class TestBPMNToWorkflowNet(unittest.TestCase):
    def test_supported_workflow_elements(self):
        for bpmn, pn_expected, case in supported_cases_workflow_bpmn:
            pn_transformed = bpmn_to_workflow_net(bpmn)
            equal, error = compare_pnml(pn_expected.net, pn_transformed.net)
            if not equal:
                save_failed_bpmn_to_pnml_transformation(
                    pn_expected, pn_transformed, bpmn, case
                )
            with self.subTest(case):
                self.assertTrue(equal, f"{case} should be equal\n{error}")


if __name__ == "__main__":
    if Path(LOG_PATH).exists():
        shutil.rmtree(LOG_PATH)
    unittest.main()
