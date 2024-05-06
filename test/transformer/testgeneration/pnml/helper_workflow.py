from transformer.pnml.pnml import (
    Place,
    Transition,
)
from transformer.pnml.workflow import WorkflowBranchingType


def create_operator_place(id: str, t: WorkflowBranchingType):
    place = Place.create(id=f"P_CENTER_{id}")
    place.mark_as_workflow_operator(t, id)
    return place


def create_operator_transition(id: str, i: int, t: WorkflowBranchingType, name: str):
    new_id = f"{id}_op_{i}"
    transition = Transition.create(id=new_id, name=name)
    transition.mark_as_workflow_operator(t, id)
    return transition
