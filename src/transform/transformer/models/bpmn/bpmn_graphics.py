from typing import Optional, Union

from pydantic_xml import attr, element

from transform.transformer.models.bpmn.base import ns_map
from transform.transformer.utility.utility import BaseModel


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
    bounds: Optional[DCBounds] = element(default=None)


class BPMNEdge(BPMNDIObject, tag="BPMNEdge"):
    waypoints: list[DIWaypoint] = element(default_factory=list)
    label: Optional[BPMNLabel] = element(default=None)


class BPMNShape(BPMNDIObject, tag="BPMNShape"):
    bounds: DCBounds
    isExpanded: Optional[bool] = attr(default=None)
    label: Optional[BPMNLabel] = element(default=None)


class BPMNPlane(BPMNDIObject, tag="BPMNPlane"):
    eles: list[Union[BPMNShape, BPMNEdge]] = element(default_factory=list)


class BPMNDiagram(BPMNDIID, tag="BPMNDiagram"):
    plane: Optional[BPMNPlane] = element(default=None)
