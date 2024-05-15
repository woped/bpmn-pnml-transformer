
from pydantic_xml import attr, element

from transformer.models.bpmn.base import ns_map
from transformer.utility.utility import BaseModel


class BPMNDINamespace(BaseModel, ns="bpmndi", nsmap=ns_map):
    pass


class BPMNDIID(BPMNDINamespace):
    id: str = attr()


class BPMNDIObject(BPMNDIID):
    bpmnElement: str = attr()


class DCBounds(BaseModel, tag="Bounds", ns="dc", nsmap=ns_map):
    x: int = attr()
    y: int = attr()
    width: int = attr()
    height: int = attr()


class DIWaypoint(BaseModel, tag="waypoint", ns="di", nsmap=ns_map):
    x: int = attr()
    y: int = attr()


class BPMNLabel(BPMNDINamespace, tag="BPMNLabel"):
    bounds: DCBounds | None = element(default=None)


class BPMNEdge(BPMNDIObject, tag="BPMNEdge"):
    waypoints: list[DIWaypoint] = element(default_factory=list)
    label: BPMNLabel | None = element(default=None)


class BPMNShape(BPMNDIObject, tag="BPMNShape"):
    bounds: DCBounds
    isExpanded: bool | None = attr(default=None)
    label: BPMNLabel | None = element(default=None)


class BPMNPlane(BPMNDIObject, tag="BPMNPlane"):
    eles: list[BPMNShape | BPMNEdge] = element(default_factory=list)


class BPMNDiagram(BPMNDIID, tag="BPMNDiagram"):
    plane: BPMNPlane | None = element(default=None)
