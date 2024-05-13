from typing import Optional

from pydantic import ValidationInfo, model_validator
from pydantic_xml import attr, element
from transformer.exceptions import NotSupportedBPMNElement
from transformer.utility.utility import BaseModel

ns_map = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
    "di": "http://www.omg.org/spec/DD/20100524/DI",
}


class BPMNNamespace(BaseModel, ns="bpmn", nsmap=ns_map):
    pass


class GenericIdNode(BPMNNamespace):
    id: str = attr()

    def __hash__(self):
        return hash((type(self),) + (self.id,))


class FlowRef(BaseModel):
    text: str


class GenericBPMNNode(GenericIdNode):
    name: Optional[str] = attr(default=None)
    incoming: set[str] = element("incoming", default_factory=set)
    outgoing: set[str] = element("outgoing", default_factory=set)

    def __hash__(self):
        return hash((type(self),) + (self.id,))

    def get_in_degree(self):
        return len(self.incoming)

    def get_out_degree(self):
        return len(self.outgoing)


class Gateway(GenericBPMNNode):
    pass


class NotSupportedNode(GenericBPMNNode):
    @model_validator(mode="before")
    def raise_unsupported_tag_exception(self, data: ValidationInfo):
        raise NotSupportedBPMNElement(
            "tag not supported", (data.config or {}).get("title")
        )
