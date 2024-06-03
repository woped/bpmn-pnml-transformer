"""Elements used as placeholder nodes to simplify transformation."""

from transformer.models.pnml.base import NetElement


class HelperPNMLElement(NetElement):
    """"""


class GatewayHelperPNML(HelperPNMLElement):
    """"""


class XORHelperPNML(GatewayHelperPNML):
    """"""


class ANDHelperPNML(GatewayHelperPNML):
    """"""
