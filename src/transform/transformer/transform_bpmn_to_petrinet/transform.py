from typing import Callable

from transformer.models.bpmn.base import GenericBPMNNode
from transformer.models.bpmn.bpmn import (
    BPMN,
    AndGateway,
    EndEvent,
    OrGateway,
    Process,
    StartEvent,
    Task,
    XorGateway,
)
from transformer.models.pnml.pnml import Place, Pnml, Transition
from transformer.transform_bpmn_to_petrinet.preprocess_bpmn.extend_process import (
    extend_subprocess,
)
from transformer.transform_bpmn_to_petrinet.preprocess_bpmn.gateway_for_workflow import (
    preprocess_gateways,
)
from transformer.transform_bpmn_to_petrinet.preprocess_bpmn.inclusive_bpmn_preprocess import (
    replace_inclusive_gateways,
)
from transformer.transform_bpmn_to_petrinet.preprocess_bpmn.insert_adjacent_subprocesses import (
    insert_temp_between_adjacent_subprocesses,
)
from transformer.transform_bpmn_to_petrinet.transform_workflow_helper import (
    handle_workflow_elements,
)
from transformer.utility.utility import create_silent_node_name


def transform_bpmn_to_petrinet(bpmn: Process, is_workflow_net: bool = False):
    pnml = Pnml.generate_empty_net(bpmn.id)
    net = pnml.net

    nodes = set(bpmn._flatten_node_typ_map())

    # find workflow specific nodes
    to_handle_as_workflow_element = {XorGateway, AndGateway, Process}
    if is_workflow_net:
        workflow_nodes: set[GenericBPMNNode] = set(
            [x for x in nodes if type(x) in to_handle_as_workflow_element]
        )
        nodes = nodes.difference(workflow_nodes)

    # handle normals nodes
    for node in nodes:
        if isinstance(node, (Task, AndGateway)):
            net.add_element(
                Transition.create(
                    id=node.id,
                    name=(
                        node.name
                        if node.name != ""
                        or node.get_in_degree() > 1
                        or node.get_out_degree() > 1
                        else None
                    ),
                )
            )
        elif isinstance(
            node, (OrGateway, XorGateway, StartEvent, EndEvent, GenericBPMNNode)
        ):
            net.add_element(Place(id=node.id))
        else:
            raise Exception(f"{type(node)} not supported")

    # handle workflow specific nodes
    if is_workflow_net and workflow_nodes:
        handle_workflow_elements(bpmn, net, workflow_nodes, transform_bpmn_to_petrinet)

    # handle remaining flows
    for flow in bpmn.flows:
        source = net.get_node_or_none(flow.sourceRef)
        target = net.get_node_or_none(flow.targetRef)
        if source is None or target is None:
            continue
        if isinstance(source, Place) and isinstance(target, Place):
            t = net.add_element(
                Transition(id=create_silent_node_name(source.id, target.id))
            )
            net.add_arc(source, t)
            net.add_arc(t, target)
        elif isinstance(source, Transition) and isinstance(target, Transition):
            p = net.add_element(Place(id=create_silent_node_name(source.id, target.id)))
            net.add_arc(source, p)
            net.add_arc(p, target)
        else:
            net.add_arc(source, target)
    return pnml


def apply_preprocessing(bpmn: Process, funcs: list[Callable[[Process], None]]):
    for p in bpmn.subprocesses:
        apply_preprocessing(p, funcs)

    for f in funcs:
        f(bpmn)


def bpmn_to_st_net(bpmn: BPMN):
    extend_subprocess(bpmn.process.subprocesses, bpmn.process)

    apply_preprocessing(bpmn.process, [replace_inclusive_gateways])

    return transform_bpmn_to_petrinet(bpmn.process)


def bpmn_to_workflow_net(bpmn: BPMN):
    apply_preprocessing(
        bpmn.process,
        [
            replace_inclusive_gateways,
            preprocess_gateways,
            insert_temp_between_adjacent_subprocesses,
        ],
    )
    return transform_bpmn_to_petrinet(bpmn.process, True)


def bpmn_to_st_net_from_xml(bpmn_xml: str):
    bpmn = BPMN.from_xml(bpmn_xml)
    return bpmn_to_st_net(bpmn)
