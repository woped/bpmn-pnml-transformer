"""Generates simple bpmn and the according petri net for multiple cases."""
from testgeneration.bpmn.utility import create_bpmn
from testgeneration.pnml.utility import create_petri_net

from transformer.models.bpmn.bpmn import (
    BPMN,
    AndGateway,
    EndEvent,
    OrGateway,
    StartEvent,
    Task,
    XorGateway,
)
from transformer.models.pnml.pnml import Place, Pnml, Transition
from transformer.utility.utility import create_silent_node_name


def start_end():
    """Returns a simple bpmn and the according petri net for a start-end scenario."""
    case = "start_end"
    se_id = "start"
    ee_id = "end"
    bpmn = create_bpmn(case, [[StartEvent(id=se_id), EndEvent(id=ee_id)]])
    net = create_petri_net(
        case,
        [
            [
                Place(id=se_id),
                Transition(id=create_silent_node_name(se_id, ee_id)),
                Place(id=ee_id),
            ]
        ],
    )
    return bpmn, net, case


def task():
    """Returns a simple bpmn and the according petri net for a task."""
    case = "task"
    se_id = "elem_1"
    ee_id = "elem_2"
    task_id = "elem_3"
    bpmn = create_bpmn(
        case,
        [[StartEvent(id=se_id), Task(id=task_id, name=task_id), EndEvent(id=ee_id)]],
    )
    net = create_petri_net(
        case,
        [
            [
                Place(id=se_id),
                Transition.create(task_id, task_id),
                Place(id=ee_id),
            ]
        ],
    )
    return bpmn, net, case


def gateway_parallel():
    """Returns a bpmn and the according petri net for a parallel (AND) sequence."""
    case = "gateway_parallel"
    se_id = "elem_1"
    ee_id = "elem_2"
    task_id = "elem_3"
    task_2_id = "elem_6"
    gw_split = "elem_4"
    gw_join = "elem_5"

    bpmn_gw_split = AndGateway(id=gw_split)
    bpmn_gw_join = AndGateway(id=gw_join)
    bpmn = create_bpmn(
        case,
        [
            [
                StartEvent(id=se_id),
                bpmn_gw_split,
                Task(id=task_id, name=task_id),
                bpmn_gw_join,
                EndEvent(id=ee_id),
            ],
            [bpmn_gw_split, Task(id=task_2_id, name=task_2_id), bpmn_gw_join],
        ],
    )

    pn_gw_split = Transition.create(gw_split)
    pn_gw_join = Transition.create(gw_join)
    net = create_petri_net(
        case,
        [
            [
                Place(id=se_id),
                pn_gw_split,
                Place(id=create_silent_node_name(gw_split, task_id)),
                Transition.create(id=task_id, name=task_id),
                Place(id=create_silent_node_name(task_id, gw_join)),
                pn_gw_join,
                Place(id=ee_id),
            ],
            [
                pn_gw_split,
                Place(id=create_silent_node_name(gw_split, task_2_id)),
                Transition.create(id=task_2_id, name=task_2_id),
                Place(id=create_silent_node_name(task_2_id, gw_join)),
                pn_gw_join,
            ],
        ],
    )
    return bpmn, net, case


def gateway_exclusive_or():
    """Returns a bpmn and the according petri net for an exclusive (XOR) sequence."""
    case = "gateway_exclusive_or"
    se_id = "elem_1"
    ee_id = "elem_2"
    task_id = "elem_3"
    task_2_id = "elem_6"
    gw_split = "elem_4"
    gw_join = "elem_5"

    bpmn_gw_split = XorGateway(id=gw_split)
    bpmn_gw_join = XorGateway(id=gw_join)
    bpmn = create_bpmn(
        case,
        [
            [
                StartEvent(id=se_id),
                bpmn_gw_split,
                Task(id=task_id, name=task_id),
                bpmn_gw_join,
                EndEvent(id=ee_id),
            ],
            [bpmn_gw_split, Task(id=task_2_id, name=task_2_id), bpmn_gw_join],
        ],
    )
    pn_gw_split = Place(id=gw_split)
    pn_gw_join = Place(id=gw_join)
    net = create_petri_net(
        case,
        [
            [
                Place(id=se_id),
                Transition(id=create_silent_node_name(se_id, gw_split)),
                pn_gw_split,
                Transition.create(id=task_id, name=task_id),
                pn_gw_join,
                Transition(id=create_silent_node_name(gw_join, ee_id)),
                Place(id=ee_id),
            ],
            [pn_gw_split, Transition.create(id=task_2_id, name=task_2_id), pn_gw_join],
        ],
    )
    return bpmn, net, case


def gateway_inclusive_or():
    """Returns a bpmn and the according petri net for an inclusive (OR) sequence."""
    case = "gateway_inclusive_or"
    se_id = "start_id"
    ee_id = "end_id"
    task_id = "task_1"
    task_2_id = "task_2"
    gw_split = "gw_split"
    gw_join = "gw_join"

    bpmn_gw_split = OrGateway(id=gw_split)
    bpmn_gw_join = OrGateway(id=gw_join)
    bpmn = create_bpmn(
        case,
        [
            [
                StartEvent(id=se_id),
                bpmn_gw_split,
                Task(id=task_id, name=task_id),
                bpmn_gw_join,
                EndEvent(id=ee_id),
            ],
            [bpmn_gw_split, Task(id=task_2_id, name=task_2_id), bpmn_gw_join],
        ],
    )
    pn_gw_split_and = Transition.create(id="OR" + bpmn_gw_split.id)
    pn_gw_join_and = Transition.create(id="OR" + bpmn_gw_join.id)

    pn_gw_split_1_xor = Place(id=pn_gw_split_and.id + task_id)
    pn_gw_split_1_join = Place(id=task_id + pn_gw_join_and.id)
    silent_1 = Transition(id=pn_gw_split_1_xor.id + pn_gw_split_1_join.id)

    pn_gw_split_2_xor = Place(id=pn_gw_split_and.id + task_2_id)
    pn_gw_split_2_join = Place(id=task_2_id + pn_gw_join_and.id)
    silent_2 = Transition(id=pn_gw_split_2_xor.id + pn_gw_split_2_join.id)

    net = create_petri_net(
        case,
        [
            [
                Place(id=se_id),
                pn_gw_split_and,
                pn_gw_split_1_xor,
                Transition.create(id=task_id, name=task_id),
                pn_gw_split_1_join,
                pn_gw_join_and,
                Place(id=ee_id),
            ],
            [
                pn_gw_split_1_xor,
                silent_1,
                pn_gw_split_1_join,
            ],
            [
                pn_gw_split_and,
                pn_gw_split_2_xor,
                Transition.create(id=task_2_id, name=task_2_id),
                pn_gw_split_2_join,
                pn_gw_join_and,
            ],
            [pn_gw_split_2_xor, silent_2, pn_gw_split_2_join],
        ],
    )
    return bpmn, net, case


def subprocess():
    """Returns a bpmn and the according petri net for subprocess scenario."""
    case = "subprocess"
    se_id = "elem_1"
    ee_id = "elem_2"

    subprocess_id = "elem_3"
    subprocess_name = "subprocess"
    # subprocess nodes
    sb_se_id = "elem_sb_1"
    sb_ee_id = "elem_sb_2"
    sb_t_id = "elem_sb_3"

    sub_bpmn = create_bpmn(
        "temp", [[StartEvent(id=sb_se_id), Task(id=sb_t_id), EndEvent(id=sb_ee_id)]]
    )
    sub_bpmn.process.id = subprocess_id
    sub_bpmn.process.name = subprocess_name

    bpmn = create_bpmn(
        case, [[StartEvent(id=se_id), sub_bpmn.process, EndEvent(id=ee_id)]]
    )

    net = create_petri_net(
        case,
        [
            [
                Place(id=se_id),
                Transition(id=create_silent_node_name(se_id, sb_se_id)),
                Place(id=sb_se_id),
                Transition(id=sb_t_id),
                Place(id=sb_ee_id),
                Transition(id=create_silent_node_name(sb_ee_id, ee_id)),
                Place(id=ee_id),
            ],
        ],
    )
    return bpmn, net, case


all_cases: list[tuple[BPMN, Pnml, str]] = [
    start_end(),
    task(),
    gateway_inclusive_or(),
    gateway_parallel(),
    gateway_exclusive_or(),
    subprocess(),
]
