"""Unit tests for the detection of subelements.

Includes tests to check whether all PNML and BPMN subelemts are identified correctly.
"""

import unittest

from transform.transformer.equality.bpmn import get_all_processes_by_id
from transform.transformer.equality.petrinet import get_all_nets_by_id
from transform.transformer.models.bpmn.bpmn import BPMN
from transform.transformer.models.pnml.pnml import Pnml


class TestSubelements(unittest.TestCase):
    """This class tests whether all subprocesses are identified."""

    def test_pnml_eqaulity_subprocess(self):
        """Tests whether all pnml subprocesses are identified."""
        pnml = Pnml.from_file("src/transform/tests/assets/multiplesubprocesses.pnml")
        subnets = {}
        get_all_nets_by_id(pnml.net, subnets)
        self.assertEqual(len(subnets), 8)

    def test_bpmn_eqaulity_subprocess(self):
        """Tests whether all bpmn subprocesses are identified."""
        bpmn = BPMN.from_file("src/transform/tests/assets/multiplesubprocesses.bpmn")
        subnets = {}
        get_all_processes_by_id(bpmn.process, subnets)
        self.assertEqual(len(subnets), 5)