"""Elements used as placeholder nodes to simplify transformation."""

from transformer.models.pnml.base import NetElement


class HelperPNMLElement(NetElement):
    """Superclass for HelperPNMLElements for transformation."""


class GatewayHelperPNML(HelperPNMLElement):
    """Superclass for Helper gateways for transformation."""


class XORHelperPNML(GatewayHelperPNML):
    """Expected to be transformed to a BPMN-XOR-Gateway."""


class ANDHelperPNML(GatewayHelperPNML):
    """Expected to be transformed to a BPMN-AND-Gateway."""
