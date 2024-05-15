
from pydantic_xml import attr, element

from transformer.models.pnml.workflow import Operator, WorkflowBranchingType
from transformer.utility.utility import WOPED, BaseModel


class GenericNetIDNode(BaseModel):
    id: str = attr()

    def __hash__(self):
        return hash((type(self),) + (self.id,))


class Coordinates(BaseModel):
    x: float = attr()
    y: float = attr()


class Graphics(BaseModel, tag="graphics"):
    offset: Coordinates | None = element("offset", default=None)
    dimension: Coordinates | None = element("dimension", default=None)
    position: Coordinates | None = element("position", default=None)


class Name(BaseModel, tag="name"):
    graphics: Graphics | None = None
    title: str | None = element(tag="text", default=None)


class Toolspecific(BaseModel, tag="toolspecific"):
    tool: str = attr(default=WOPED)
    version: str = attr(default="1.0")

    # normal transition
    time: str | None = element(tag="time", default=None)
    timeUnit: str | None = element(tag="timeUnit", default=None)
    orientation: str | None = element(tag="orientation", default=None)

    # wf-operator
    operator: Operator | None = None

    # arc
    probability: str | None = element(tag="probability", default=None)
    displayProbabilityOn: str | None = element(
        tag="displayProbabilityOn", default=None
    )
    displayProbabilityPosition: Coordinates | None = None

    # subprocess
    subprocess: bool | None = element(tag="subprocess", default=None)

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
    name: Name | None = None
    graphics: Graphics | None = None
    toolspecific: Toolspecific | None = None

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
