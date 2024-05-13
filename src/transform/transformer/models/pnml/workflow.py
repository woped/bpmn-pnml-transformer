from enum import Enum

from pydantic_xml import attr

from transformer.utility.utility import BaseModel


class WorkflowBranchingType(int, Enum):
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
    id: str = attr()
    type: WorkflowBranchingType = attr()
