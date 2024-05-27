"""PNML Extensions for BaseModel."""

from pydantic_xml import attr, element

from transform.transformer.models.pnml.workflow import Operator, WorkflowBranchingType
from transform.transformer.utility.utility import WOPED, BaseModel


class GenericNetIDNode(BaseModel):
    """Generic Petri net node extension of BaseModel (+ID)."""
    id: str = attr()

    def __hash__(self):
        """Return hash of this instance."""
        return hash((type(self),) + (self.id,))


class Coordinates(BaseModel):
    """Coordinate extension of BaseModel (+x and y)."""
    x: float = attr()
    y: float = attr()


class Graphics(BaseModel, tag="graphics"):
    """Graphics extension of BaseModel (+offset, dimension, position)."""
    offset: Coordinates | None = element("offset", default=None)
    dimension: Coordinates | None = element("dimension", default=None)
    position: Coordinates | None = element("position", default=None)


class Name(BaseModel, tag="name"):
    """Name extension of BaseModel (+graphics, title)."""
    graphics: Graphics | None = None
    title: str | None = element(tag="text", default=None)


class Toolspecific(BaseModel, tag="toolspecific"):
    """Toolspecific extension of BaseModel (+tool, version, transition,operator...)."""
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
        """Returns whether instance is a workflow operator."""
        if self.tool == WOPED and self.operator:
            return True
        return False

    def is_workflow_subprocess(self):
        """Returns whether instance is a workflow subprocess."""
        if self.tool == WOPED and self.subprocess:
            return True
        return False


class GenericNetNode(GenericNetIDNode):
    """Generic NetNode extension of net id node."""
    pass


class NetElement(GenericNetNode):
    """Generic NetElement extension of GenericNetNode (+name, graphics, toolspecific)."""
    name: Name | None = None
    graphics: Graphics | None = None
    toolspecific: Toolspecific | None = None

    def get_name(self):
        """Returns name of instance."""
        if not self.name:
            return None
        return self.name.title

    def __hash__(self):
        """Return instance hashed."""
        return hash((type(self),) + (self.id,))

    def is_workflow_operator(self):
        """Return whether instance is workflow operator."""
        if not self.toolspecific:
            return False
        return self.toolspecific.is_workflow_operator()

    def is_workflow_subprocess(self):
        """Returns whether instance is workflow subprocess."""
        if not self.toolspecific:
            return False
        return self.toolspecific.is_workflow_subprocess()

    def mark_as_workflow_operator(self, type: WorkflowBranchingType, id: str):
        """Mark this instance as workflow operator."""
        t = self
        if not t.toolspecific:
            t.toolspecific = Toolspecific()
        t.toolspecific.operator = Operator(id=id, type=type)

    def mark_as_workflow_subprocess(self):
        """Mark this instance as a subprocess."""
        t = self
        if not t.toolspecific:
            t.toolspecific = Toolspecific()
        t.toolspecific.subprocess = True
        return self


class Inscription(BaseModel, tag="inscription"):
    """Inscription extension of BaseModel (+text, graphics)."""
    text: str = element(tag="text")
    graphics: Graphics
