"""Initiate the preprocessing and transformation of pnml to bpmn."""
from collections.abc import Callable

from transformer.models.bpmn.base import Gateway
from transformer.models.bpmn.bpmn import (
    BPMN,
    AndGateway,
    EndEvent,
    Process,
    StartEvent,
    Task,
    XorGateway,
)
from transformer.models.pnml.pnml import Net, Place, Pnml, Transition
from transformer.transform_petrinet_to_bpmn.workflow_helper import (
    find_workflow_operators,
    find_workflow_subprocesses,
    handle_workflow_operators,
    handle_workflow_subprocesses,
)

from transformer.transform_petrinet_to_bpmn.preprocess_pnml import (
    split_different_operator as sdo
)
split_different_operators = sdo.split_different_operators


def remove_silent_tasks(bpmn: Process):
    """Remove silent tasks (Without name)."""
    for task in bpmn.tasks.copy():
        if task.name is not None:
            continue
        source_id, target_id = bpmn.remove_node_with_connecting_flows(task)
        bpmn.add_flow(bpmn.get_node(source_id), bpmn.get_node(target_id))


def remove_unnecessary_gateways(bpmn: Process):
    """Remove unnecessary gateways (In and out degree <= 1)."""
    gw_nodes = {
        node for node in bpmn._flatten_node_typ_map() if issubclass(type(node), Gateway)
    }
    for gw_node in gw_nodes:
        if gw_node.get_in_degree() > 1 or gw_node.get_out_degree() > 1:
            continue
        source_id, target_id = bpmn.remove_node_with_connecting_flows(gw_node)
        bpmn.add_flow(bpmn.get_node(source_id), bpmn.get_node(target_id))


def transform_petrinet_to_bpmn(net: Net):
    """Initiate the transformation of a preprocessed petri net to bpmn."""
    bpmn_general = BPMN.generate_empty_bpmn(net.id or "new_net")
    bpmn = bpmn_general.process

    transitions = net.transitions.copy()
    places = net.places.copy()

    # find workflow specific elements
    to_handle_subprocesses = find_workflow_subprocesses(net)
    transitions.difference_update(to_handle_subprocesses)

    to_handle_operators = find_workflow_operators(net)
    for operator_wrapper in to_handle_operators:
        for operator_node in operator_wrapper.nodes:
            if isinstance(operator_node, Place):
                places.remove(operator_node)
            elif isinstance(operator_node, Transition):
                transitions.remove(operator_node)
            else:
                raise Exception()

    # handle normal places
    for place in places:
        in_degree, out_degree = net.get_in_degree(place), net.get_out_degree(place)
        if in_degree == 0:
            bpmn.add_node(StartEvent(id=place.id))
        elif out_degree == 0:
            bpmn.add_node(EndEvent(id=place.id))
        else:
            bpmn.add_node(XorGateway(id=place.id))

    # handle normal transitions
    for transition in transitions:
        in_degree, out_degree = (
            net.get_in_degree(transition),
            net.get_out_degree(transition),
        )
        if in_degree == 0 or out_degree == 0:
            raise Exception("what to do with transition source/sink")
        elif in_degree == 1 and out_degree == 1:
            bpmn.add_node(Task(id=transition.id, name=transition.get_name()))
        else:
            bpmn.add_node(AndGateway(id=transition.id, name=transition.get_name()))

    # handle workflow specific elements
    handle_workflow_subprocesses(
        net, bpmn, to_handle_subprocesses, transform_petrinet_to_bpmn
    )
    handle_workflow_operators(net, bpmn, to_handle_operators)

    # handle remaining arcs
    for arc in net.arcs:
        source_in_nodes = arc.source in net._temp_elements
        target_in_nodes = arc.target in net._temp_elements
        if not source_in_nodes or not target_in_nodes:
            continue
        source = bpmn.get_node(arc.source)
        target = bpmn.get_node(arc.target)
        bpmn.add_flow(source, target)

    # Postprocessing
    remove_silent_tasks(bpmn)
    remove_unnecessary_gateways(bpmn)

    return bpmn_general


def apply_preprocessing(net: Net, funcs: list[Callable[[Net], None]]):
    """Preprocess the whole petri net."""
    for p in net.pages:
        apply_preprocessing(p.net, funcs)

    for f in funcs:
        f(net)


def pnml_to_bpmn(pnml: Pnml):
    """Process and transform a petri net to bpmn."""
    net = pnml.net

    apply_preprocessing(net, [split_different_operators])

    return transform_petrinet_to_bpmn(net)
