"""BPMNDI based objects."""
from pydantic_xml import attr, element

from transformer.models.bpmn.base import ns_map
from transformer.utility.utility import BaseModel


class BPMNDINamespace(BaseModel, ns="bpmndi", nsmap=ns_map):
    """BPMNDINNamespace extension of BaseModel."""
    pass


class BPMNDIID(BPMNDINamespace):
    """BPMNDIID extension of BPMNDINamespace with string xml attribute."""
    id: str = attr()


class BPMNDIObject(BPMNDIID):
    """BPMNDIObject extension of BPMNDIID with element xml attribute."""
    bpmnElement: str = attr()


class DCBounds(BaseModel, tag="Bounds", ns="dc", nsmap=ns_map):
    """DCBounds extension of BaseModel with x,y, width and height xml attributes."""
    x: int = attr()
    y: int = attr()
    width: int = attr()
    height: int = attr()


class DIWaypoint(BaseModel, tag="waypoint", ns="di", nsmap=ns_map):
    """DIWaypoint extension of BaseModel with x and y xml attribute."""
    x: int = attr()
    y: int = attr()


class BPMNLabel(BPMNDINamespace, tag="BPMNLabel"):
    """BPMNLabel extension of BPMNIDNamespace with DCBounds attribute."""
    bounds: DCBounds | None = element(default=None)


class BPMNEdge(BPMNDIObject, tag="BPMNEdge"):
    """BPMNEdge extension of BPMNDIObject with waypoints and label."""
    waypoints: list[DIWaypoint] = element(default_factory=list)
    label: BPMNLabel | None = element(default=None)


class BPMNShape(BPMNDIObject, tag="BPMNShape"):
    """BPMNShape extension of BPMNDIObject with bounds, isExpanded and label attr.."""
    bounds: DCBounds
    isExpanded: bool | None = attr(default=None)
    label: BPMNLabel | None = element(default=None)


class BPMNPlane(BPMNDIObject, tag="BPMNPlane"):
    """BPMNPlane extension of BPMNDIObject with element list as attribute."""
    eles: list[BPMNShape | BPMNEdge] = element(default_factory=list)


class BPMNDiagram(BPMNDIID, tag="BPMNDiagram"):
    """BPMNDiagram extension of BPMNDIID with plane as attribute."""
    plane: BPMNPlane | None = element(default=None)
