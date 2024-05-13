from testgeneration.bpmn.utility import create_bpmn
from testgeneration.pnml.utility import create_petri_net
from testgeneration.utility import UniqueIDGenerator

from transformer.models.bpmn.bpmn import (
    BPMN,
    AndGateway,
    EndEvent,
    StartEvent,
    Task,
    XorGateway,
)
from transformer.models.pnml.pnml import Place, Pnml, Transition
from transformer.utility.utility import create_silent_node_name


def start_end():
    case = "start_end"
    se_id = UniqueIDGenerator.generate()
    ee_id = UniqueIDGenerator.generate()

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

    bpmn = create_bpmn(case, [[StartEvent(id=se_id), EndEvent(id=ee_id)]])

    return bpmn, net, case


def normal_transition():
    case = "normal_transition"
    se_id = UniqueIDGenerator.generate()
    ee_id = UniqueIDGenerator.generate()
    task_id = UniqueIDGenerator.generate()
    net = create_petri_net(
        case,
        [
            [
                Place(id=se_id),
                Transition.create(id=task_id, name=task_id),
                Place(id=ee_id),
            ]
        ],
    )
    bpmn = create_bpmn(
        case,
        [[StartEvent(id=se_id), Task(id=task_id, name=task_id), EndEvent(id=ee_id)]],
    )
    return bpmn, net, case


def and_transition():
    case = "and_transition"
    se_id = UniqueIDGenerator.generate()
    ee_id = UniqueIDGenerator.generate()
    task_id = UniqueIDGenerator.generate()
    task_2_id = UniqueIDGenerator.generate()
    gw_split = UniqueIDGenerator.generate()
    gw_join = UniqueIDGenerator.generate()

    pn_gw_split = Transition.create(id=gw_split, name=gw_split)
    pn_gw_join = Transition.create(id=gw_join, name=gw_join)
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

    bpmn_gw_split = AndGateway(id=gw_split, name=gw_split)
    bpmn_gw_join = AndGateway(id=gw_join, name=gw_join)
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
    return bpmn, net, case


def xor_place():
    case = "xor_place"
    se_id = UniqueIDGenerator.generate()
    ee_id = UniqueIDGenerator.generate()
    task_id = UniqueIDGenerator.generate()
    task_2_id = UniqueIDGenerator.generate()
    gw_split = UniqueIDGenerator.generate()
    gw_join = UniqueIDGenerator.generate()

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
    return bpmn, net, case


all_cases: list[tuple[BPMN, Pnml, str]] = [
    start_end(),
    normal_transition(),
    and_transition(),
    xor_place(),
]
