"""Generate supported test cases for Workflow transformations."""
from testgeneration.bpmn.utility import create_bpmn
from testgeneration.pnml.helper_workflow import (
    create_operator_place,
    create_operator_transition,
)
from testgeneration.pnml.utility import create_petri_net

from transform.transformer.models.bpmn.bpmn import (
    BPMN,
    AndGateway,
    EndEvent,
    StartEvent,
    Task,
    XorGateway,
)
from transform.transformer.models.pnml.pnml import Page, Place, Pnml, Transition
from transform.transformer.models.pnml.workflow import WorkflowBranchingType
from transform.transformer.utility.utility import create_silent_node_name


def gateway_parallel_join_split():
    """Return a BPMN and workflow net with AND gates."""
    case = "parallel_workflow_elements"
    se_id = "elem_1"
    ee_id = "elem_2"

    task_1 = "elem_3"
    task_11 = "elem_6"
    task_2 = "elem_30"
    task_22 = "elem_60"

    gw_split = "elem_4"
    gw_join = "elem_5"
    gw_both = "elem_7"

    and_split = create_operator_transition(
        gw_split, 1, WorkflowBranchingType.AndSplit, gw_split
    )
    and_join_split = create_operator_transition(
        gw_both, 1, WorkflowBranchingType.AndJoinSplit, gw_both
    )
    and_join = create_operator_transition(
        gw_join, 1, WorkflowBranchingType.AndJoin, gw_join
    )

    net = create_petri_net(
        case,
        [
            [
                Place.create(id=se_id),
                and_split,
                Place.create(id=create_silent_node_name(and_split.id, task_1)),
                Transition.create(id=task_1, name=task_1),
                Place.create(id=create_silent_node_name(task_1, and_join_split.id)),
                and_join_split,
                Place.create(id=create_silent_node_name(and_join_split.id, task_2)),
                Transition.create(id=task_2, name=task_2),
                Place.create(id=create_silent_node_name(task_2, and_join.id)),
                and_join,
                Place.create(id=ee_id),
            ],
            [
                and_split,
                Place.create(id=create_silent_node_name(and_split.id, task_11)),
                Transition.create(id=task_11, name=task_11),
                Place.create(id=create_silent_node_name(task_11, and_join_split.id)),
                and_join_split,
            ],
            [
                and_join_split,
                Place.create(id=create_silent_node_name(and_join_split.id, task_22)),
                Transition.create(id=task_22, name=task_22),
                Place.create(id=create_silent_node_name(task_22, and_join.id)),
                and_join,
            ],
        ],
    )

    bpmn_gw_split = AndGateway(id=gw_split, name=gw_split)
    bpmn_gw_both = AndGateway(id=gw_both, name=gw_both)
    bpmn_gw_join = AndGateway(id=gw_join, name=gw_join)

    bpmn = create_bpmn(
        case,
        [
            [
                StartEvent(id=se_id),
                bpmn_gw_split,
                Task(id=task_1, name=task_1),
                bpmn_gw_both,
                Task(id=task_2, name=task_2),
                bpmn_gw_join,
                EndEvent(id=ee_id),
            ],
            [bpmn_gw_split, Task(id=task_11, name=task_11), bpmn_gw_both],
            [bpmn_gw_both, Task(id=task_22, name=task_22), bpmn_gw_join],
        ],
    )

    return bpmn, net, case


def gateway_exclusive_join_split():
    """Return a BPMN and workflow net with XOR gates."""
    case = "exclusive_workflow_elements"
    se_id = "elem_1"
    ee_id = "elem_2"

    task_1 = "elem_3"
    task_11 = "elem_6"
    task_2 = "elem_30"
    task_22 = "elem_60"

    gw_split = "elem_4"
    gw_join = "elem_5"
    gw_both = "elem_7"

    xor_split_1 = create_operator_transition(
        gw_split, 1, WorkflowBranchingType.XorSplit, gw_split
    )
    xor_split_2 = create_operator_transition(
        gw_split, 2, WorkflowBranchingType.XorSplit, gw_split
    )

    xor_join_split_place = create_operator_place(
        gw_both, WorkflowBranchingType.XorJoinSplit
    )
    xor_join_split_in_1 = create_operator_transition(
        gw_both, 1, WorkflowBranchingType.XorJoinSplit, gw_both
    )
    xor_join_split_in_2 = create_operator_transition(
        gw_both, 2, WorkflowBranchingType.XorJoinSplit, gw_both
    )
    xor_join_split_out_1 = create_operator_transition(
        gw_both, 3, WorkflowBranchingType.XorJoinSplit, gw_both
    )
    xor_join_split_out_2 = create_operator_transition(
        gw_both, 4, WorkflowBranchingType.XorJoinSplit, gw_both
    )

    xor_join_1 = create_operator_transition(
        gw_join, 1, WorkflowBranchingType.XorJoin, gw_join
    )
    xor_join_2 = create_operator_transition(
        gw_join, 2, WorkflowBranchingType.XorJoin, gw_join
    )

    start = Place.create(id=se_id)
    end = Place.create(id=ee_id)
    net = create_petri_net(
        case,
        [
            [
                start,
                xor_split_1,
                Place.create(id=create_silent_node_name(xor_split_1.id, task_1)),
                Transition.create(id=task_1, name=task_1),
                Place.create(
                    id=create_silent_node_name(task_1, xor_join_split_in_1.id)
                ),
                xor_join_split_in_1,
                xor_join_split_place,
                xor_join_split_out_1,
                Place.create(
                    id=create_silent_node_name(xor_join_split_out_1.id, task_2)
                ),
                Transition.create(id=task_2, name=task_2),
                Place.create(id=create_silent_node_name(task_2, xor_join_1.id)),
                xor_join_1,
                end,
            ],
            [
                start,
                xor_split_2,
                Place.create(id=create_silent_node_name(xor_split_2.id, task_11)),
                Transition.create(id=task_11, name=task_11),
                Place.create(
                    id=create_silent_node_name(task_11, xor_join_split_in_2.id)
                ),
                xor_join_split_in_2,
                xor_join_split_place,
                xor_join_split_out_2,
                Place.create(
                    id=create_silent_node_name(xor_join_split_out_2.id, task_22)
                ),
                Transition.create(id=task_22, name=task_22),
                Place.create(id=create_silent_node_name(task_22, xor_join_2.id)),
                xor_join_2,
                end,
            ],
        ],
    )

    bpmn_gw_split = XorGateway(id=gw_split, name=gw_split)
    bpmn_gw_both = XorGateway(id=gw_both, name=gw_both)
    bpmn_gw_join = XorGateway(id=gw_join, name=gw_join)

    bpmn = create_bpmn(
        case,
        [
            [
                StartEvent(id=se_id),
                bpmn_gw_split,
                Task(id=task_1, name=task_1),
                bpmn_gw_both,
                Task(id=task_2, name=task_2),
                bpmn_gw_join,
                EndEvent(id=ee_id),
            ],
            [bpmn_gw_split, Task(id=task_11, name=task_11), bpmn_gw_both],
            [bpmn_gw_both, Task(id=task_22, name=task_22), bpmn_gw_join],
        ],
    )

    return bpmn, net, case


def gateway_side_by_side_xor_and():
    """Return a BPMN and workflow net with XOR+AND gates."""
    case = "gateway_side_by_side_xor_and"
    se_id = "elem_1"
    ee_id = "elem_2"

    task_1 = "elem_3"
    task_11 = "elem_6"
    task_2 = "elem_30"
    task_22 = "elem_60"

    gw_split_start = "elem_4"
    gw_join_start = "elem_8"
    gw_split_end = "elem_7"
    gw_join_end = "elem_5"

    # Xor Part
    xor_split_1 = create_operator_transition(
        gw_split_start, 1, WorkflowBranchingType.XorSplit, gw_split_start
    )
    xor_split_2 = create_operator_transition(
        gw_split_start, 2, WorkflowBranchingType.XorSplit, gw_split_start
    )
    xor_join_1 = create_operator_transition(
        gw_join_start, 1, WorkflowBranchingType.XorJoin, gw_join_start
    )
    xor_join_2 = create_operator_transition(
        gw_join_start, 2, WorkflowBranchingType.XorJoin, gw_join_start
    )
    # And Part
    and_split = create_operator_transition(
        gw_split_end, 1, WorkflowBranchingType.AndSplit, gw_split_end
    )
    and_join = create_operator_transition(
        gw_join_end, 1, WorkflowBranchingType.AndJoin, gw_join_end
    )

    gateway_merge_place = Place.create(id=gw_join_start + gw_split_end)

    start = Place.create(id=se_id)
    end = Place.create(id=ee_id)
    net = create_petri_net(
        case,
        [
            [
                start,
                xor_split_1,
                Place.create(id=create_silent_node_name(xor_split_1.id, task_1)),
                Transition.create(id=task_1, name=task_1),
                Place.create(id=create_silent_node_name(task_1, xor_join_1.id)),
                xor_join_1,
                gateway_merge_place,
                and_split,
                Place.create(id=create_silent_node_name(and_split.id, task_2)),
                Transition.create(id=task_2, name=task_2),
                Place.create(id=create_silent_node_name(task_2, and_join.id)),
                and_join,
                end,
            ],
            [
                start,
                xor_split_2,
                Place.create(id=create_silent_node_name(xor_split_2.id, task_11)),
                Transition.create(id=task_11, name=task_11),
                Place.create(id=create_silent_node_name(task_11, xor_join_2.id)),
                xor_join_2,
                gateway_merge_place,
            ],
            [
                and_split,
                Place.create(id=create_silent_node_name(and_split.id, task_22)),
                Transition.create(id=task_22, name=task_22),
                Place.create(id=create_silent_node_name(task_22, and_join.id)),
                and_join,
            ],
        ],
    )

    bpmn_gw_split_start = XorGateway(id=gw_split_start, name=gw_split_start)
    bpmn_gw_join_start = XorGateway(id=gw_join_start, name=gw_join_start)
    bpmn_gw_split_end = AndGateway(id=gw_split_end, name=gw_split_end)
    bpmn_gw_join_end = AndGateway(id=gw_join_end, name=gw_join_end)

    bpmn = create_bpmn(
        case,
        [
            [
                StartEvent(id=se_id),
                bpmn_gw_split_start,
                Task(id=task_1, name=task_1),
                bpmn_gw_join_start,
                bpmn_gw_split_end,
                Task(id=task_2, name=task_2),
                bpmn_gw_join_end,
                EndEvent(id=ee_id),
            ],
            [bpmn_gw_split_start, Task(id=task_11, name=task_11), bpmn_gw_join_start],
            [bpmn_gw_split_end, Task(id=task_22, name=task_22), bpmn_gw_join_end],
        ],
    )

    return bpmn, net, case


def gateway_side_by_side_and_xor():
    """Return a BPMN and workflow net with AND+XOR gates."""
    case = "gateway_side_by_side_and_xor"
    se_id = "elem_1"
    ee_id = "elem_2"

    task_1 = "elem_3"
    task_11 = "elem_6"
    task_2 = "elem_30"
    task_22 = "elem_60"

    gw_split_start = "elem_4"
    gw_join_start = "elem_8"
    gw_split_end = "elem_7"
    gw_join_end = "elem_5"

    # And Part
    and_split = create_operator_transition(
        gw_split_start, 1, WorkflowBranchingType.AndSplit, gw_split_start
    )
    and_join = create_operator_transition(
        gw_join_start, 1, WorkflowBranchingType.AndJoin, gw_join_start
    )
    # Xor Part
    xor_split_1 = create_operator_transition(
        gw_split_end, 1, WorkflowBranchingType.XorSplit, gw_split_end
    )
    xor_split_2 = create_operator_transition(
        gw_split_end, 2, WorkflowBranchingType.XorSplit, gw_split_end
    )
    xor_join_1 = create_operator_transition(
        gw_join_end, 1, WorkflowBranchingType.XorJoin, gw_join_end
    )
    xor_join_2 = create_operator_transition(
        gw_join_end, 2, WorkflowBranchingType.XorJoin, gw_join_end
    )

    gateway_merge_place = Place.create(id=gw_join_start + gw_split_end)

    start = Place.create(id=se_id)
    end = Place.create(id=ee_id)
    net = create_petri_net(
        case,
        [
            [
                start,
                and_split,
                Place.create(id=create_silent_node_name(and_split.id, task_1)),
                Transition.create(id=task_1, name=task_1),
                Place.create(id=create_silent_node_name(task_1, and_join.id)),
                and_join,
                gateway_merge_place,
                xor_split_1,
                Place.create(id=create_silent_node_name(xor_split_1.id, task_2)),
                Transition.create(id=task_2, name=task_2),
                Place.create(id=create_silent_node_name(task_2, xor_join_1.id)),
                xor_join_1,
                end,
            ],
            [
                and_split,
                Place.create(id=create_silent_node_name(and_split.id, task_11)),
                Transition.create(id=task_11, name=task_11),
                Place.create(id=create_silent_node_name(task_11, and_join.id)),
                and_join,
            ],
            [
                gateway_merge_place,
                xor_split_2,
                Place.create(id=create_silent_node_name(xor_split_2.id, task_22)),
                Transition.create(id=task_22, name=task_22),
                Place.create(id=create_silent_node_name(task_22, xor_join_2.id)),
                xor_join_2,
                end,
            ],
        ],
    )

    bpmn_gw_split_start = AndGateway(id=gw_split_start, name=gw_split_start)
    bpmn_gw_join_start = AndGateway(id=gw_join_start, name=gw_join_start)
    bpmn_gw_split_end = XorGateway(id=gw_split_end, name=gw_split_end)
    bpmn_gw_join_end = XorGateway(id=gw_join_end, name=gw_join_end)

    bpmn = create_bpmn(
        case,
        [
            [
                StartEvent(id=se_id),
                bpmn_gw_split_start,
                Task(id=task_1, name=task_1),
                bpmn_gw_join_start,
                bpmn_gw_split_end,
                Task(id=task_2, name=task_2),
                bpmn_gw_join_end,
                EndEvent(id=ee_id),
            ],
            [bpmn_gw_split_start, Task(id=task_11, name=task_11), bpmn_gw_join_start],
            [bpmn_gw_split_end, Task(id=task_22, name=task_22), bpmn_gw_join_end],
        ],
    )
    return bpmn, net, case


def xor_and_split():
    """Return a BPMN and workflow net with mixed gates."""
    case = "gateway_xor_and_split"
    se_id = "elem_1"
    ee_id = "elem_2"

    task_1 = "elem_3"
    task_11 = "elem_6"
    task_2 = "elem_30"
    task_22 = "elem_60"

    gw_split_start = "elem_4"
    gw_join_end = "elem_5"

    gw_both = "elem_both"

    # Xor Part
    xor_split_1 = create_operator_transition(
        gw_split_start, 1, WorkflowBranchingType.XorSplit, gw_split_start
    )
    xor_split_2 = create_operator_transition(
        gw_split_start, 2, WorkflowBranchingType.XorSplit, gw_split_start
    )

    linking_place = create_operator_place(
        gw_both, WorkflowBranchingType.XorJoinAndSplit
    )
    xor_join_and_split_in_1 = create_operator_transition(
        gw_both, 1, WorkflowBranchingType.XorJoinAndSplit, gw_both
    )
    xor_join_and_split_in_2 = create_operator_transition(
        gw_both, 2, WorkflowBranchingType.XorJoinAndSplit, gw_both
    )
    xor_join_and_split_out = create_operator_transition(
        gw_both, 3, WorkflowBranchingType.XorJoinAndSplit, gw_both
    )
    # And Part
    and_join = create_operator_transition(
        gw_join_end, 1, WorkflowBranchingType.AndJoin, gw_join_end
    )

    start = Place.create(id=se_id)
    end = Place.create(id=ee_id)
    net = create_petri_net(
        case,
        [
            [
                start,
                xor_split_1,
                Place.create(id=create_silent_node_name(xor_split_1.id, task_1)),
                Transition.create(id=task_1, name=task_1),
                Place.create(
                    id=create_silent_node_name(task_1, xor_join_and_split_in_1.id)
                ),
                xor_join_and_split_in_1,
                linking_place,
                xor_join_and_split_out,
                Place.create(
                    id=create_silent_node_name(xor_join_and_split_out.id, task_2)
                ),
                Transition.create(id=task_2, name=task_2),
                Place.create(id=create_silent_node_name(task_2, and_join.id)),
                and_join,
                end,
            ],
            [
                start,
                xor_split_2,
                Place.create(id=create_silent_node_name(xor_split_2.id, task_11)),
                Transition.create(id=task_11, name=task_11),
                Place.create(
                    id=create_silent_node_name(task_11, xor_join_and_split_in_2.id)
                ),
                xor_join_and_split_in_2,
                linking_place,
            ],
            [
                xor_join_and_split_out,
                Place.create(
                    id=create_silent_node_name(xor_join_and_split_out.id, task_22)
                ),
                Transition.create(id=task_22, name=task_22),
                Place.create(id=create_silent_node_name(task_22, and_join.id)),
                and_join,
            ],
        ],
    )

    bpmn_gw_split_start = XorGateway(id=gw_split_start, name=gw_split_start)
    bpmn_gw_join_start = XorGateway(id="XOR" + gw_both, name=gw_both)
    bpmn_gw_split_end = AndGateway(id="AND" + gw_both, name=gw_both)
    bpmn_gw_join_end = AndGateway(id=gw_join_end, name=gw_join_end)

    bpmn = create_bpmn(
        case,
        [
            [
                StartEvent(id=se_id),
                bpmn_gw_split_start,
                Task(id=task_1, name=task_1),
                bpmn_gw_join_start,
                bpmn_gw_split_end,
                Task(id=task_2, name=task_2),
                bpmn_gw_join_end,
                EndEvent(id=ee_id),
            ],
            [bpmn_gw_split_start, Task(id=task_11, name=task_11), bpmn_gw_join_start],
            [bpmn_gw_split_end, Task(id=task_22, name=task_22), bpmn_gw_join_end],
        ],
    )

    return bpmn, net, case


def and_xor_split():
    """Return a BPMN and workflow net with mixed gates."""
    case = "gateway_and_xor_split"
    se_id = "elem_1"
    ee_id = "elem_2"

    task_1 = "elem_3"
    task_11 = "elem_6"
    task_2 = "elem_30"
    task_22 = "elem_60"

    gw_xor_join_start = "elem_4"
    gw_and_split_start = "elem_5"

    gw_both = "elem_both"

    # Xor Part
    xor_join_1 = create_operator_transition(
        gw_xor_join_start, 1, WorkflowBranchingType.XorSplit, gw_xor_join_start
    )
    xor_join_2 = create_operator_transition(
        gw_xor_join_start, 2, WorkflowBranchingType.XorSplit, gw_xor_join_start
    )
    # Inner Part
    linking_place = create_operator_place(
        gw_both, WorkflowBranchingType.AndJoinXorSplit
    )
    and_join_xor_split_in = create_operator_transition(
        gw_both, 1, WorkflowBranchingType.AndJoinXorSplit, gw_both
    )
    and_join_xor_split_out_1 = create_operator_transition(
        gw_both, 2, WorkflowBranchingType.AndJoinXorSplit, gw_both
    )
    and_join_xor_split_out_2 = create_operator_transition(
        gw_both, 3, WorkflowBranchingType.AndJoinXorSplit, gw_both
    )
    # And Part
    and_split = create_operator_transition(
        gw_and_split_start, 1, WorkflowBranchingType.AndJoin, gw_and_split_start
    )

    start = Place.create(id=se_id)
    end = Place.create(id=ee_id)
    net = create_petri_net(
        case,
        [
            [
                start,
                and_split,
                Place.create(id=create_silent_node_name(and_split.id, task_1)),
                Transition.create(id=task_1, name=task_1),
                Place.create(
                    id=create_silent_node_name(task_1, and_join_xor_split_in.id)
                ),
                and_join_xor_split_in,
                linking_place,
                and_join_xor_split_out_1,
                Place.create(
                    id=create_silent_node_name(and_join_xor_split_out_1.id, task_2)
                ),
                Transition.create(id=task_2, name=task_2),
                Place.create(id=create_silent_node_name(task_2, xor_join_1.id)),
                xor_join_1,
                end,
            ],
            [
                and_split,
                Place.create(id=create_silent_node_name(and_split.id, task_11)),
                Transition.create(id=task_11, name=task_11),
                Place.create(id=create_silent_node_name(task_11, xor_join_2.id)),
                and_join_xor_split_in,
            ],
            [
                linking_place,
                and_join_xor_split_out_2,
                Place.create(
                    id=create_silent_node_name(and_join_xor_split_out_2.id, task_22)
                ),
                Transition.create(id=task_22, name=task_22),
                Place.create(id=create_silent_node_name(task_22, xor_join_1.id)),
                xor_join_2,
                end,
            ],
        ],
    )

    bpmn_gw_split_start = AndGateway(id=gw_and_split_start, name=gw_and_split_start)
    bpmn_gw_join_start = AndGateway(id="AND" + gw_both, name=gw_both)
    bpmn_gw_split_end = XorGateway(id="XOR" + gw_both, name=gw_both)
    bpmn_gw_join_end = XorGateway(id=gw_xor_join_start, name=gw_xor_join_start)

    bpmn = create_bpmn(
        case,
        [
            [
                StartEvent(id=se_id),
                bpmn_gw_split_start,
                Task(id=task_1, name=task_1),
                bpmn_gw_join_start,
                bpmn_gw_split_end,
                Task(id=task_2, name=task_2),
                bpmn_gw_join_end,
                EndEvent(id=ee_id),
            ],
            [bpmn_gw_split_start, Task(id=task_11, name=task_11), bpmn_gw_join_start],
            [bpmn_gw_split_end, Task(id=task_22, name=task_22), bpmn_gw_join_end],
        ],
    )

    return bpmn, net, case


def subprocess():
    """Return a BPMN and workflow net with a subprocess."""
    case = "subprocess"
    se_id = "elem_1"
    ee_id = "elem_2"

    subprocess_id = "elem_3"
    subprocess_name = "subprocess"
    # subprocess nodes
    sb_t_id = "elem_sb_3"

    net = create_petri_net(
        case,
        [
            [
                Place(id=se_id),
                Transition.create(
                    subprocess_id, subprocess_name
                ).mark_as_workflow_subprocess(),
                Place(id=ee_id),
            ],
        ],
    )
    #
    net_page = Page(
        id=subprocess_id,
        net=create_petri_net(
            "",
            [
                [
                    Place(id=se_id),
                    Transition.create(id=sb_t_id, name=sb_t_id),
                    Place(id=ee_id),
                ]
            ],
        ).net,
    )
    net_page.net.id = subprocess_id
    net.net.add_page(net_page)

    sub_bpmn = create_bpmn(
        "temp",
        [[StartEvent(id=se_id), Task(id=sb_t_id, name=sb_t_id), EndEvent(id=ee_id)]],
    )
    sub_bpmn.process.id = subprocess_id
    sub_bpmn.process.name = subprocess_name

    bpmn = create_bpmn(
        case, [[StartEvent(id=se_id), sub_bpmn.process, EndEvent(id=ee_id)]]
    )

    return bpmn, net, case


supported_cases_workflow_pnml: list[tuple[BPMN, Pnml, str]] = [
    gateway_parallel_join_split(),
    gateway_exclusive_join_split(),
    gateway_side_by_side_xor_and(),
    gateway_side_by_side_and_xor(),
    xor_and_split(),
    and_xor_split(),
    subprocess(),
]
