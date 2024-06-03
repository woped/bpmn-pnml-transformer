"""Methods to initiate a bpmn to petri net transformation."""

from collections.abc import Callable

from transformer.models.bpmn.base import Gateway, GenericBPMNNode
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
from transformer.transform_bpmn_to_petrinet.preprocess_bpmn import (
    inclusive_bpmn_preprocess as ibp,
)
from transformer.transform_bpmn_to_petrinet.preprocess_bpmn import (
    insert_adjacent_mapped_transition as ias,
)
from transformer.transform_bpmn_to_petrinet.preprocess_bpmn.extend_process import (
    extend_subprocess,
)
from transformer.transform_bpmn_to_petrinet.preprocess_bpmn.gateway_for_workflow import ( # noqa: E501
    preprocess_gateways,
)
from transformer.transform_bpmn_to_petrinet.transform_workflow_helper import (
    handle_gateways,
    handle_subprocesses,
)
from transformer.utility.utility import create_silent_node_name

<<<<<<< HEAD
from transformer.transform_bpmn_to_petrinet.preprocess_bpmn import (
    inclusive_bpmn_preprocess as ibp,
    insert_adjacent_subprocesses as ias
)


=======
>>>>>>> origin/main
replace_inclusive_gateways = ibp.replace_inclusive_gateways
insert_temp_between_adjacent_mapped_transitions = (
    ias.insert_temp_between_adjacent_mapped_transition
)


def transform_bpmn_to_petrinet(bpmn: Process, is_workflow_net: bool = False):
    """Transform a BPMN to ST or WOPED workflow Net."""
    pnml = Pnml.generate_empty_net(bpmn.id)
    net = pnml.net

    nodes = set(bpmn._flatten_node_typ_map())

    # find workflow specific nodes
    to_handle_gateways: list[Gateway] = []
    to_handle_subprocesses: list[Process] = []

    if is_workflow_net:
        for node in nodes:
            if isinstance(node, Process):
                to_handle_subprocesses.append(node)
            elif isinstance(node, Gateway):
                to_handle_gateways.append(node)
        nodes = nodes.difference(to_handle_gateways, to_handle_subprocesses)

    # handle normals nodes
    for node in nodes:
        if isinstance(node, Task | AndGateway):
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
            node, OrGateway | XorGateway | StartEvent | EndEvent | GenericBPMNNode
        ):
            net.add_element(Place(id=node.id))
        else:
            raise Exception(f"{type(node)} not supported")

    # handle workflow specific nodes
    if is_workflow_net and (to_handle_gateways or to_handle_subprocesses):
        handle_subprocesses(
            net, bpmn, to_handle_subprocesses, transform_bpmn_to_petrinet
        )
        handle_gateways(net, bpmn, to_handle_gateways)

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
    """Recursively apply preprocessing to each process and subprocess."""
    for p in bpmn.subprocesses:
        apply_preprocessing(p, funcs)

    for f in funcs:
        f(bpmn)


def bpmn_to_st_net(bpmn: BPMN):
    """Return a processed and transformed ST-net of process."""
    extend_subprocess(bpmn.process.subprocesses, bpmn.process)

    apply_preprocessing(bpmn.process, [replace_inclusive_gateways])

    return transform_bpmn_to_petrinet(bpmn.process)


def bpmn_to_workflow_net(bpmn: BPMN):
    """Return a processed and transformed workflow net of process."""
    apply_preprocessing(
        bpmn.process,
        [
            replace_inclusive_gateways,
            preprocess_gateways,
            insert_temp_between_adjacent_mapped_transitions,
        ],
    )
    return transform_bpmn_to_petrinet(bpmn.process, True)


def bpmn_to_st_net_from_xml(bpmn_xml: str):
    """Return a processed and transformed workflow net of process from xml file."""
    bpmn = BPMN.from_xml(bpmn_xml)
    return bpmn_to_st_net(bpmn)
