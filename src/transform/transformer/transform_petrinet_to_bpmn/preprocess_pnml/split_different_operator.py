"""Module for splitting combined workflow operators in Petri nets.

This module provides functionality to split combined workflow operators (And-Xor, 
Xor-And) in Petri nets into individual workflow operators, as these combined operators 
cannot be handled by BPMN elements.
"""

from transformer.models.pnml.pnml import Net, Place
from transformer.models.pnml.workflow import WorkflowBranchingType
from transformer.transform_bpmn_to_petrinet.transform_workflow_helper import (
    add_wf_and_join,
    add_wf_and_split,
    add_wf_xor_join,
    add_wf_xor_split,
)
from transformer.transform_petrinet_to_bpmn.workflow_helper import (
    find_workflow_operators,
)


def split_different_operators(net: Net):
    """Combined Workflowoperators (And-Xor, Xor-And) can't be handled by BPMN-Elements.

    -> Split them into individual Workflowoperators
    """
    wf_operators = [
        x
        for x in find_workflow_operators(net)
        if x.t
        in {
            WorkflowBranchingType.AndJoinXorSplit,
            WorkflowBranchingType.XorJoinAndSplit,
        }
    ]
    for o in wf_operators:
        p = net.add_element(Place.create(id="LINK_WF_OPERATOR" + o.id))
        # split combined operator into 2 individual
        if o.t == WorkflowBranchingType.AndJoinXorSplit:
            add_wf_and_join(
                net=net,
                id="AND" + o.id,
                name=o.name,
                out_place=p,
                in_places=list(o.incoming_nodes),
            )
            add_wf_xor_split(
                net=net,
                id="XOR" + o.id,
                name=o.name,
                in_place=p,
                out_places=list(o.outgoing_nodes),
            )
        elif o.t == WorkflowBranchingType.XorJoinAndSplit:
            add_wf_xor_join(
                net=net,
                id="XOR" + o.id,
                name=o.name,
                out_place=p,
                in_places=list(o.incoming_nodes),
            )
            add_wf_and_split(
                net=net,
                id="AND" + o.id,
                name=o.name,
                in_place=p,
                out_places=list(o.outgoing_nodes),
            )
        else:
            raise Exception("invalid")
        # remove all original arcs and nodes from net
        for node in o.nodes:
            net.remove_element(node)
        for arc in o.all_arcs:
            net.remove_arc(arc)
