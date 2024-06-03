"""Handle workflow subprocesses and operators of petri net and handle them in bpmn."""

from collections.abc import Callable

from pydantic import BaseModel, Field

from transformer.models.bpmn.base import GenericBPMNNode
from transformer.models.bpmn.bpmn import BPMN, AndGateway, Process, XorGateway
from transformer.models.pnml.base import NetElement
from transformer.models.pnml.pnml import Arc, Net, Page, Transition
from transformer.models.pnml.transform_helper import (
    ANDHelperPNML,
    GatewayHelperPNML,
    XORHelperPNML,
)
from transformer.models.pnml.workflow import WorkflowBranchingType


class WorkflowOperatorWrapper(BaseModel):
    """WorkflowOperatorWrapper extension of BaseModel (+ID, name, type, nodes...)."""

    id: str
    name: str | None = None
    t: WorkflowBranchingType

    # all operator nodes
    nodes: list[NetElement] = Field(default_factory=list)
    # non-opeartor nodes connected to opeartor nodes
    incoming_nodes: set[NetElement] = Field(default_factory=set)
    outgoing_nodes: set[NetElement] = Field(default_factory=set)
    # arcs onnceting non-operator nodes to operator nodes
    incoming_arcs: set[Arc] = Field(default_factory=set)
    outgoing_arcs: set[Arc] = Field(default_factory=set)
    # arcs connected to operator nodes
    all_arcs: set[Arc] = Field(default_factory=set)

    def get_copy_unique_in_arcs(self):
        already_added_sources = set()
        arcs: list[Arc] = []
        for arc in self.incoming_arcs:
            if arc.source in already_added_sources:
                continue
            already_added_sources.add(arc.source)
            arcs.append(arc.model_copy())
        return arcs

    def get_copy_unique_out_arcs(self):
        already_added_targets = set()
        arcs: list[Arc] = []
        for arc in self.outgoing_arcs:
            if arc.target in already_added_targets:
                continue
            already_added_targets.add(arc.target)
            arcs.append(arc.model_copy())
        return arcs


def find_workflow_subprocesses(net: Net):
    """Return all workflow subprocesses of a net."""
    return [e for e in net.transitions if e.is_workflow_subprocess()]


def find_workflow_operators(net: Net):
    """Return all workflow operators of a net."""
    operator_map: dict[str, list[NetElement]] = {}
    for node in net._temp_elements.values():
        if isinstance(node, Page):
            continue
        if not node.is_workflow_operator():
            continue
        if not node.toolspecific or not node.toolspecific.operator:
            raise Exception("invalid")
        op_id = node.toolspecific.operator.id
        if op_id not in operator_map:
            operator_map[op_id] = []
        operator_map[op_id].append(node)
    operator_wrappers: list[WorkflowOperatorWrapper] = []
    for op_id, operators in operator_map.items():
        o = WorkflowOperatorWrapper(
            t=operators[0].toolspecific.operator.type,  # type: ignore
            nodes=operators,
            id=operators[0].toolspecific.operator.id,  # type: ignore
            name=operators[0].get_name(),
        )
        operator_wrappers.append(o)

        for operator in operators:
            for incoming in net.get_incoming(operator.id):
                o.all_arcs.add(incoming)
                if net.get_element(incoming.source) in operators:
                    continue
                o.incoming_nodes.add(net.get_element(incoming.source))
                o.incoming_arcs.add(incoming)

            for outgoing in net.get_outgoing(operator.id):
                o.all_arcs.add(outgoing)
                if net.get_element(outgoing.target) in operators:
                    continue
                o.outgoing_nodes.add(net.get_element(outgoing.target))
                o.outgoing_arcs.add(outgoing)
    return operator_wrappers


def handle_workflow_subprocesses(
    net: Net,
    bpmn: Process,
    to_handle_subprocesses: list[Transition],
    caller_func: Callable[[Net], BPMN],
):
    """Add all found workflow subprocesses of a net as nodes to a bpmn."""
    for subprocess_transition in to_handle_subprocesses:
        sb_id = subprocess_transition.id
        page = net.get_page(sb_id)
        page_net = page.net

        outer_source_id = list(net.get_incoming(sb_id))[0].source
        outer_sink_id = list(net.get_outgoing(sb_id))[0].target

        inner_source_id, inner_sink_id = (
            page_net.get_element(outer_source_id),
            page_net.get_element(outer_sink_id),
        )

        if (
            page_net.get_in_degree(inner_source_id) > 0
            or page_net.get_out_degree(inner_sink_id) > 0
        ):
            raise Exception(
                "currently source/sink in subprocess must have no incoming/outgoing arcs"
                " to convert to BPMN Start and Endevents"
            )

        inner_bpmn = caller_func(page_net).process
        inner_bpmn.id = sb_id
        inner_bpmn.name = subprocess_transition.get_name()
        inner_bpmn.isExecutable = None
        bpmn.add_node(inner_bpmn)


def handle_workflow_operators(
    net: Net, bpmn: Process, to_handle_temp_gateways: list[GatewayHelperPNML]
):
    """Add all found workflow operators of a net as nodes to a bpmn."""
    for temp_gateway in to_handle_temp_gateways:
        if isinstance(temp_gateway, XORHelperPNML):
            bpmn.add_node(XorGateway(id=temp_gateway.id, name=temp_gateway.get_name()))
        elif isinstance(temp_gateway, ANDHelperPNML):
            bpmn.add_node(AndGateway(id=temp_gateway.id, name=temp_gateway.get_name()))
