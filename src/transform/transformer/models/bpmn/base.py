"""BPMN objects and extensions."""

from pydantic import ValidationInfo, model_validator
from pydantic_xml import attr, element

from transformer.exceptions import NotSupportedBPMNElement
from transformer.utility.utility import BaseBPMNModel

ns_map = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
}


class BPMNNamespace(BaseBPMNModel, ns="bpmn", nsmap=ns_map):
    """Extension of BaseBPMNModel with namespace bpmn and namespace map."""


class GenericIdNode(BPMNNamespace):
    """Extension of BPMNNamespace with id attribute and hash method."""

    id: str = attr()

    def __hash__(self):
        """Returns a hash of this instance."""
        return hash((type(self),) + (self.id,))


class FlowRef(BaseBPMNModel):
    """Extension of BaseBPMNModel."""

    text: str


class GenericBPMNNode(GenericIdNode):
    """BPMN extension of GenericIdNode with name, incoming and outgoing attribute."""

    name: str | None = attr(default=None)
    incoming: set[str] = element("incoming", default_factory=set)
    outgoing: set[str] = element("outgoing", default_factory=set)

    def __hash__(self):
        """Returns a hash of this instance."""
        return hash((type(self),) + (self.id,))

    def get_in_degree(self):
        """Returns incoming degree of this instance."""
        return len(self.incoming)

    def get_out_degree(self):
        """Returns outgoing degree of this instance."""
        return len(self.outgoing)


class Gateway(GenericBPMNNode):
    """Gateway extension of BPMN node."""


class NotSupportedNode(GenericBPMNNode):
    """NotSupportedNode extension of BPMN node."""

    @model_validator(mode="before")
    def raise_unsupported_tag_exception(self, data: ValidationInfo):
        """Raises exception for unsupported tags."""
        raise NotSupportedBPMNElement(
            "tag not supported", (data.config or {}).get("title")
        )
