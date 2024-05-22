"""Helper methods for bpmn to pnml (Workflow operators and elements)."""
from typing import cast
from collections.abc import Callable

from transformer.models.bpmn.base import GenericBPMNNode
from transformer.models.bpmn.bpmn import AndGateway, Process, XorGateway
from transformer.models.pnml.base import NetElement
from transformer.models.pnml.pnml import (
    Net,
    Page,
    Place,
    Pnml,
    Transition,
)
from transformer.models.pnml.workflow import WorkflowBranchingType
from transformer.utility.bpmn import find_end_events, find_start_events
from transformer.utility.utility import create_arc_name, create_silent_node_name


def create_workflow_operator_helper_transition(
    net: Net, id: str, name: str | None, i: int, t: WorkflowBranchingType
):
    """Return a transition as a workflow operator helper element."""
    transition = net.add_element(Transition.create(id=f"{id}_op_{i}", name=name))
    transition.mark_as_workflow_operator(t, id)
    return transition


def add_arc(net: Net, source: NetElement, target: NetElement):
    """Add arc between source and target net elements for a net."""
    if type(source) is not type(target):
        net.add_arc(source, target, create_arc_name(source.id, target.id))
    elif isinstance(source, Place):
        t = net.add_element(
            Transition.create(create_silent_node_name(source.id, target.id))
        )
        net.add_arc(source, t, create_arc_name(source.id, t.id))
        net.add_arc(t, target, create_arc_name(t.id, target.id))
    elif isinstance(source, Transition):
        # check if actually name was used to create place or original id was used for id
        p = net.add_element(Place.create(create_silent_node_name(source.id, target.id)))
        net.add_arc(source, p, create_arc_name(source.id, p.id))
        net.add_arc(p, target, create_arc_name(p.id, target.id))
    else:
        raise Exception("invalid petrinet node")


def add_wf_xor_split(
    net: Net,
    in_place: NetElement,
    out_places: list[NetElement],
    id: str,
    name: str | None,
):
    """Add workflow xor split for in place and out places."""
    for i, out in enumerate(out_places):
        t = create_workflow_operator_helper_transition(
            net, id, name, i + 1, WorkflowBranchingType.XorSplit
        )
        add_arc(net, in_place, t)
        add_arc(net, t, out)


def add_wf_xor_join(
    net: Net,
    out_place: NetElement,
    in_places: list[NetElement],
    id: str,
    name: str | None,
):
    """Add workflow xor join for  in places and out place."""
    for i, in_place in enumerate(in_places):
        t = create_workflow_operator_helper_transition(
            net, id, name, i + 1, WorkflowBranchingType.XorJoin
        )
        add_arc(net, in_place, t)
        add_arc(net, t, out_place)


def add_wf_and_split(
    net: Net,
    in_place: NetElement,
    out_places: list[NetElement],
    id: str,
    name: str | None,
):
    """Add workflow and split for in place and out places."""
    t = create_workflow_operator_helper_transition(
        net, id, name, 1, WorkflowBranchingType.AndSplit
    )
    add_arc(net, in_place, t)
    for out in out_places:
        add_arc(net, t, out)


def add_wf_and_join(
    net: Net,
    out_place: NetElement,
    in_places: list[NetElement],
    id: str,
    name: str | None,
):
    """Add workflow and join for  in places and out place."""
    t = create_workflow_operator_helper_transition(
        net, id, name, 1, WorkflowBranchingType.AndJoin
    )
    add_arc(net, t, out_place)
    for in_place in in_places:
        add_arc(net, in_place, t)


def add_wf_xor_split_join(
    net: Net,
    in_places: list[NetElement],
    out_places: list[NetElement],
    id: str,
    name: str | None,
):
    """Add workflow xor split-join for in places and out places."""
    linking_place = net.add_element(Place.create(id=f"P_CENTER_{id}"))
    linking_place.mark_as_workflow_operator(WorkflowBranchingType.XorJoinSplit, id)

    for i, in_place in enumerate(in_places):
        t = create_workflow_operator_helper_transition(
            net, id, name, i + 1, WorkflowBranchingType.XorJoinSplit
        )
        add_arc(net, in_place, t)
        add_arc(net, t, linking_place)

    for i, out in enumerate(out_places):
        t = create_workflow_operator_helper_transition(
            net, id, name, i + 1 + len(in_places), WorkflowBranchingType.XorJoinSplit
        )
        add_arc(net, t, out)
        add_arc(net, linking_place, t)


def add_wf_and_split_join(
    net: Net,
    in_places: list[NetElement],
    out_places: list[NetElement],
    id: str,
    name: str | None,
):
    """Add workflow and split-join for in places and out places."""
    t = create_workflow_operator_helper_transition(
        net, id, name, 1, WorkflowBranchingType.AndJoinSplit
    )
    for in_place in in_places:
        add_arc(net, in_place, t)
    for out in out_places:
        add_arc(net, t, out)


type_map = {
    XorGateway: (add_wf_xor_split, add_wf_xor_join, add_wf_xor_split_join),
    AndGateway: (add_wf_and_split, add_wf_and_join, add_wf_and_split_join),
}


def handle_workflow_operators(net: Net, bpmn: Process, node: GenericBPMNNode) -> bool:
    """Handle given operator for a bpmn process to petri net process."""
    node_type = type(node)
    f_split, f_join, f_split_join = type_map[node_type]  # type: ignore
    in_degree, out_degree = node.get_in_degree(), node.get_out_degree()
    in_flows, out_flows = bpmn.get_incoming(node.id), bpmn.get_outgoing(node.id)
    source_ids, target_ids = (
        [f.sourceRef for f in in_flows],
        [f.targetRef for f in out_flows],
    )
    for id in [*in_flows, *out_flows]:
        bpmn.remove_flow(id)

    net_sources = sorted(
        [cast(NetElement, net.get_element(x)) for x in source_ids], key=lambda x: x.id
    )
    net_targets = sorted(
        [cast(NetElement, net.get_element(x)) for x in target_ids], key=lambda x: x.id
    )
    # split
    if in_degree == 1:
        f_split(
            net,
            net_sources[0],
            net_targets,
            node.id,
            node.name,
        )
    # join
    elif out_degree == 1:
        f_join(net, net_targets[0], net_sources, node.id, node.name)
    # split and join
    else:
        f_split_join(net, net_sources, net_targets, node.id, node.name)
    return True


def handle_workflow_elements(
    bpmn: Process,
    net: Net,
    workflow_nodes: set[GenericBPMNNode],
    caller_func: Callable[[Process, bool], Pnml],
):
    """Handle given workflow element for a bpmn process to petri net process."""
    for node in workflow_nodes:
        if isinstance(node, Process):
            if node.get_in_degree() != 1 and node.get_out_degree != 1:
                raise Exception(
                    "Subprocess must have exactly one in and outgoing flow!"
                )

            subprocess_transition = net.add_element(
                Transition.create(node.id, node.name).mark_as_workflow_subprocess()
            )

            # WOPED subprocess start and endplaces must have the same id as the incoming/
            #outgoing node of the subprocess
            outer_in_id, outer_out_id = (
                list(bpmn.get_incoming(node.id))[0].sourceRef,
                list(bpmn.get_outgoing(node.id))[0].targetRef,
            )
            outer_in, outer_out = (
                net.get_element(outer_in_id),
                net.get_element(outer_out_id),
            )
            # if incoming/outgoing is from type transition a place will inserted after
            #the handling of the workflow elements
            # -> actual id of subprocess start/endevents must have id of new place
            if isinstance(outer_in, Transition):
                outer_in_id = create_silent_node_name(
                    outer_in.id, subprocess_transition.id
                )
            if isinstance(outer_out, Transition):
                outer_out_id = create_silent_node_name(
                    subprocess_transition.id, outer_out.id
                )

            sub_se, sub_ee = find_start_events(node)[0], find_end_events(node)[0]
            node.change_node_id(sub_se, outer_in_id)
            node.change_node_id(sub_ee, outer_out_id)

            # transform inner subprocess
            inner_net = caller_func(node, True).net
            inner_net.id = None

            net.add_page(Page(id=node.id, net=inner_net))
        else:
            handle_workflow_operators(net, bpmn, node)
