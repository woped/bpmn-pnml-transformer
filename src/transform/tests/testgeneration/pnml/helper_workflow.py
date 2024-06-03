"""Module for creating operator places and transitions in a workflow using PNML."""

from transformer.models.pnml.pnml import (
    Place,
    Transition,
)
from transformer.models.pnml.workflow import WorkflowBranchingType


def create_operator_place(id: str, t: WorkflowBranchingType):
    """Returns an operator place for a workflow operator."""
    place = Place.create(id=f"P_CENTER_{id}")
    place.mark_as_workflow_operator(t, id)
    return place


def create_operator_transition(id: str, i: int, t: WorkflowBranchingType, name: str):
    """Returns an operator transition for a workflow operator."""
    new_id = f"{id}_op_{i}"
    transition = Transition.create(id=new_id, name=name)
    transition.mark_as_workflow_operator(t, id)
    return transition
