from typing import Optional

from pydantic_xml import attr, element

from transform.transformer.models.pnml.workflow import Operator, WorkflowBranchingType
from transform.transformer.utility.utility import WOPED, BaseModel


class GenericNetIDNode(BaseModel):
    id: str = attr()

    def __hash__(self):
        return hash((type(self),) + (self.id,))


class Coordinates(BaseModel):
    x: float = attr()
    y: float = attr()


class Graphics(BaseModel, tag="graphics"):
    offset: Optional[Coordinates] = element("offset", default=None)
    dimension: Optional[Coordinates] = element("dimension", default=None)
    position: Optional[Coordinates] = element("position", default=None)


class Name(BaseModel, tag="name"):
    graphics: Optional[Graphics] = None
    title: Optional[str] = element(tag="text", default=None)


class Toolspecific(BaseModel, tag="toolspecific"):
    tool: str = attr(default=WOPED)
    version: str = attr(default="1.0")

    # normal transition
    time: Optional[str] = element(tag="time", default=None)
    timeUnit: Optional[str] = element(tag="timeUnit", default=None)
    orientation: Optional[str] = element(tag="orientation", default=None)

    # wf-operator
    operator: Optional[Operator] = None

    # arc
    probability: Optional[str] = element(tag="probability", default=None)
    displayProbabilityOn: Optional[str] = element(
        tag="displayProbabilityOn", default=None
    )
    displayProbabilityPosition: Optional[Coordinates] = None

    # subprocess
    subprocess: Optional[bool] = element(tag="subprocess", default=None)

    def is_workflow_operator(self):
        if self.tool == WOPED and self.operator:
            return True
        return False

    def is_workflow_subprocess(self):
        if self.tool == WOPED and self.subprocess:
            return True
        return False


class GenericNetNode(GenericNetIDNode):
    pass


class NetElement(GenericNetNode):
    name: Optional[Name] = None
    graphics: Optional[Graphics] = None
    toolspecific: Optional[Toolspecific] = None

    def get_name(self):
        if not self.name:
            return None
        return self.name.title

    def __hash__(self):
        return hash((type(self),) + (self.id,))

    def is_workflow_operator(self):
        if not self.toolspecific:
            return False
        return self.toolspecific.is_workflow_operator()

    def is_workflow_subprocess(self):
        if not self.toolspecific:
            return False
        return self.toolspecific.is_workflow_subprocess()

    def mark_as_workflow_operator(self, type: WorkflowBranchingType, id: str):
        t = self
        if not t.toolspecific:
            t.toolspecific = Toolspecific()
        t.toolspecific.operator = Operator(id=id, type=type)

    def mark_as_workflow_subprocess(self):
        t = self
        if not t.toolspecific:
            t.toolspecific = Toolspecific()
        t.toolspecific.subprocess = True
        return self


class Inscription(BaseModel, tag="inscription"):
    text: str = element(tag="text")
    graphics: Graphics
