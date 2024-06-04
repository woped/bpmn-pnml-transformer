"""BaseModels for BPMN-XML-Mappings."""

from pydantic_xml import attr, element

from transformer.models.pnml.workflow import (
    Operator,
    TransitionResource,
    Trigger,
    TriggerType,
    WorkflowBranchingType,
)
from transformer.utility.utility import WOPED, BaseModel


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
    """WOPED Toolspecific extension of BaseModel."""

    tool: str = attr(default=WOPED)
    version: str = attr(default="1.0")

    # normal transition
    time: str | None = element(tag="time", default=None)
    timeUnit: str | None = element(tag="timeUnit", default=None)
    orientation: str | None = element(tag="orientation", default=None)

    # wf-operator
    operator: Operator | None = None

    # traigger type
    trigger: Trigger | None = None

    # transition resource
    transitionResource: TransitionResource | None = None

    # arc
    probability: str | None = element(tag="probability", default=None)
    displayProbabilityOn: str | None = element(tag="displayProbabilityOn", default=None)
    displayProbabilityPosition: Coordinates | None = None

    # subprocess
    subprocess: bool | None = element(tag="subprocess", default=None)

    def _is_woped(self):
        return self.tool == WOPED

    def is_workflow_operator(self):
        """Returns whether instance is a workflow operator."""
        return self._is_woped() and self.operator

    def is_workflow_subprocess(self):
        """Returns whether instance is a workflow subprocess."""
        return self._is_woped() and self.subprocess

    def is_workflow_message(self):
        """Returns whether instance is a workflow message trigger."""
        return (
            self._is_woped()
            and self.transitionResource
            and self.transitionResource.roleName is TriggerType.Message
        )

    def is_workflow_time(self):
        """Returns whether instance is a workflow time trigger."""
        return (
            self._is_woped()
            and self.transitionResource
            and self.transitionResource.roleName is TriggerType.Time
        )

    def is_workflow_resource(self):
        """Returns whether instance is a workflow resource trigger."""
        return (
            self._is_woped()
            and self.transitionResource
            and self.transitionResource.roleName is TriggerType.Resource
        )

    def is_workflow_event_trigger(self):
        """Returns whether instance is a trigger."""
        return self.is_workflow_message() and self.is_workflow_time()


class GenericNetNode(GenericNetIDNode):
    """Generic NetNode extension of net id node."""


class NetElement(GenericNetNode):
    """NetElement extension of GenericNetNode (+name, graphics, toolspecific)."""

    name: Name | None = None
    graphics: Graphics | None = None
    toolspecific: Toolspecific | None = None

    def get_name(self):
        """Returns name of instance."""
        if not self.name:
            return None
        return self.name.title

    def set_copy_of_exisiting_toolspecific(self, tool: Toolspecific | None):
        """Set a copy of a existing Toolspecific instance."""
        if not tool:
            return self
        self.toolspecific = tool.model_copy()
        return self

    def __hash__(self):
        """Return instance hashed by type and id."""
        return hash((type(self),) + (self.id,))

    def is_workflow_operator(self):
        """Return whether instance is workflow operator."""
        if not self.toolspecific:
            return False
        return self.toolspecific.is_workflow_operator()

    def is_workflow_resource(self):
        """Return whether instance is workflow resource."""
        if not self.toolspecific:
            return False
        return self.toolspecific.is_workflow_resource()

    def is_workflow_message(self):
        """Return whether instance is workflow message."""
        if not self.toolspecific:
            return False
        return self.toolspecific.is_workflow_message()

    def is_workflow_time(self):
        """Return whether instance is workflow time."""
        if not self.toolspecific:
            return False
        return self.toolspecific.is_workflow_time()

    def is_workflow_event_trigger(self):
        """Return whether instance is workflow trigger."""
        if not self.toolspecific:
            return False
        return self.toolspecific.is_workflow_event_trigger()

    def is_workflow_subprocess(self):
        """Returns whether instance is workflow subprocess."""
        if not self.toolspecific:
            return False
        return self.toolspecific.is_workflow_subprocess()

    def mark_as_workflow_operator(self, type: WorkflowBranchingType, id: str):
        """Mark this instance as workflow operator."""
        if not self.toolspecific:
            self.toolspecific = Toolspecific()
        self.toolspecific.operator = Operator(id=id, type=type)
        return self

    def mark_as_workflow_subprocess(self):
        """Mark this instance as a subprocess."""
        if not self.toolspecific:
            self.toolspecific = Toolspecific()
        self.toolspecific.subprocess = True
        return self

    def mark_as_workflow_resource(self, role_name: str):
        """Mark this instance as a resource."""
        if not self.toolspecific:
            self.toolspecific = Toolspecific()

        self.toolspecific.trigger = Trigger(id="", type=TriggerType.Resource)
        self.toolspecific.transitionResource = TransitionResource(roleName=role_name)
        return self

    def mark_as_workflow_message(self):
        """Mark this instance as a message."""
        if not self.toolspecific:
            self.toolspecific = Toolspecific()
        self.toolspecific.trigger = Trigger(id="", type=TriggerType.Message)
        return self

    def mark_as_workflow_time(self):
        """Mark this instance as a time."""
        if not self.toolspecific:
            self.toolspecific = Toolspecific()
        self.toolspecific.trigger = Trigger(id="", type=TriggerType.Time)
        return self


class Inscription(BaseModel, tag="inscription"):
    """Inscription extension of BaseModel (+text, graphics)."""

    text: str = element(tag="text")
    graphics: Graphics
