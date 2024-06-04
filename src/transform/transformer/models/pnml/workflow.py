"""Petri net workflow operators."""

from enum import Enum

from pydantic_xml import attr, element

from transformer.utility.utility import BaseModel


class WorkflowBranchingType(int, Enum):
    """Workflow type definition."""

    AndSplit = 101
    AndJoin = 102
    XorSplit = 104
    XorJoin = 105
    XorJoinSplit = 106
    AndJoinSplit = 107
    # Not supported by BPMN -> Split necessary
    AndJoinXorSplit = 108
    XorJoinAndSplit = 109


class Operator(BaseModel, tag="operator"):
    """Operator extension of BaseModel (+id, type)."""

    id: str = attr()
    type: WorkflowBranchingType = attr()


class TriggerType(int, Enum):
    """Trigger type definition."""

    Resource = 200
    Message = 201
    Time = 202


class Position(BaseModel, tag="position"):
    """Placeholder Position."""

    x: str = attr()
    y: str = attr()


class Dimension(BaseModel, tag="dimension"):
    """Placeholder Dimension."""

    x: str = attr()
    y: str = attr()


class Graphics(BaseModel, tag="graphics"):
    """Placeholder Graphics."""

    position: Position = element(default=Position(x="0", y="0"))
    dimension: Dimension = element(default=Dimension(x="20", y="20"))


class Trigger(BaseModel, tag="trigger"):
    """Trigger extension of BaseModel (+id, type)."""

    id: str = attr()
    type: TriggerType = attr()

    graphics: Graphics = element(default=Graphics())


class TransitionResource(BaseModel, tag="transitionResource"):
    """Transition Resource extension of BaseModel."""

    roleName: str = attr()
    organizationalUnitName: str = attr()
