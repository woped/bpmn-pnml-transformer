"""Preprocess combined workflow operators to individual workflow operators."""

from transformer.models.pnml.base import Name
from transformer.models.pnml.pnml import Net, Transition
from transformer.models.pnml.transform_helper import (
    ANDHelperPNML,
    GatewayHelperPNML,
    XORHelperPNML,
)
from transformer.models.pnml.workflow import WorkflowBranchingType
from transformer.transform_petrinet_to_bpmn.workflow_helper import (
    WorkflowOperatorWrapper,
    find_workflow_operators,
)
from transformer.utility.pnml import generate_explicit_transition_id


def extract_task():
    pass


def handle_combined_operator(net: Net, wo: WorkflowOperatorWrapper):
    incoming_arcs = wo.get_copy_unique_in_arcs()
    outgoing_arcs = wo.get_copy_unique_out_arcs()

    for existing_arc in wo.all_arcs:
        net.remove_arc(existing_arc)
    for existing_node in wo.nodes:
        net.remove_element(existing_node)

    firstGatewayPart: GatewayHelperPNML | None = None
    secondGatewayPart: GatewayHelperPNML | None = None
    # Split mixed gateways into 2 individual gateways
    if wo.t in [
        WorkflowBranchingType.AndJoinXorSplit,
        WorkflowBranchingType.XorJoinAndSplit,
    ]:
        firstGatewayPart = (
            XORHelperPNML(id="XOR" + wo.id, name=Name(title=wo.name))
            if wo.t == WorkflowBranchingType.XorJoinAndSplit
            else ANDHelperPNML(id="AND" + wo.id, name=Name(title=wo.name))
        )
        secondGatewayPart = (
            ANDHelperPNML(id="AND" + wo.id, name=Name(title=wo.name))
            if wo.t == WorkflowBranchingType.XorJoinAndSplit
            else XORHelperPNML(id="XOR" + wo.id, name=Name(title=wo.name))
        )
    # Replace or split same gateway depending on if is implicit task
    else:
        firstGatewayPart = (
            XORHelperPNML(id=wo.id, name=Name(title=wo.name))
            if wo.t == WorkflowBranchingType.XorJoinSplit
            else ANDHelperPNML(id=wo.id, name=Name(title=wo.name))
        )
        #  If gateway with implicit task (name not None)
        # TODO
        if wo.name and False:
            secondGatewayPart = (
                XORHelperPNML(id="OUTXOR" + wo.id, name=Name(title=wo.name))
                if wo.t == WorkflowBranchingType.XorJoinSplit
                else ANDHelperPNML(id="OUTAND" + wo.id, name=Name(title=wo.name))
            )
            firstGatewayPart.id = (
                "IN" + "XOR"
                if wo.t == WorkflowBranchingType.XorJoinSplit
                else "AND" + firstGatewayPart.id
            )

    if not secondGatewayPart:
        secondGatewayPart = firstGatewayPart

    net.add_element(firstGatewayPart)
    net.add_element(secondGatewayPart)

    for new_arc in incoming_arcs:
        net.add_arc_from_id(new_arc.source, firstGatewayPart.id, new_arc.id)

    for new_arc in outgoing_arcs:
        net.add_arc_from_id(secondGatewayPart.id, new_arc.target, new_arc.id)

    if firstGatewayPart is not secondGatewayPart:
        net.add_arc_from_id(firstGatewayPart.id, secondGatewayPart.id)


def handle_single_operator(net: Net, wo: WorkflowOperatorWrapper):
    incoming_arcs = wo.get_copy_unique_in_arcs()
    outgoing_arcs = wo.get_copy_unique_out_arcs()

    for existing_arc in wo.all_arcs:
        net.remove_arc(existing_arc)
    for existing_node in wo.nodes:
        net.remove_element(existing_node)

    new_gateway = (
        XORHelperPNML(id=wo.id, name=Name(title=wo.name))
        if wo.t in [WorkflowBranchingType.XorJoin, WorkflowBranchingType.XorSplit]
        else ANDHelperPNML(id=wo.id, name=Name(title=wo.name))
    )

    net.add_element(new_gateway)
    for new_arc in incoming_arcs:
        net.add_arc_from_id(
            source_id=new_arc.source, target_id=new_gateway.id, id=new_arc.id
        )
    for new_arc in outgoing_arcs:
        net.add_arc_from_id(
            source_id=new_gateway.id, target_id=new_arc.target, id=new_arc.id
        )

    # Operator without name doesnt has an implicit task
    if not wo.name:
        return

    # Join needs task after operator
    if wo.t in [WorkflowBranchingType.AndJoin, WorkflowBranchingType.XorJoin]:
        outgoing_arc = list(net.get_outgoing(new_gateway.id))[0]
        explicit_task = Transition.create(
            id=generate_explicit_transition_id(new_gateway.id),
            name=new_gateway.get_name(),
        )
        net.add_element(explicit_task)
        net.add_arc(new_gateway, explicit_task)
        net.add_arc_from_id(explicit_task.id, outgoing_arc.target)

        net.remove_arc(outgoing_arc)
    # Split needs task before operator
    else:
        incoming_arc = list(net.get_incoming(new_gateway.id))[0]
        explicit_task = Transition.create(
            id=generate_explicit_transition_id(new_gateway.id),
            name=new_gateway.get_name(),
        )
        net.add_element(explicit_task)
        net.add_arc(explicit_task, new_gateway)
        net.add_arc_from_id(
            incoming_arc.source,
            explicit_task.id,
        )

        net.remove_arc(incoming_arc)


def handle_workflow_operators(net: Net):
    """Handle workflowoperators by replacing them with temp nodes and extracting task."""
    wf_operators = find_workflow_operators(net)
    for o in wf_operators:
        if o.t in [
            WorkflowBranchingType.AndJoin,
            WorkflowBranchingType.AndSplit,
            WorkflowBranchingType.XorJoin,
            WorkflowBranchingType.XorSplit,
        ]:
            handle_single_operator(net, o)
        elif o.t in [
            WorkflowBranchingType.AndJoinXorSplit,
            WorkflowBranchingType.XorJoinAndSplit,
            WorkflowBranchingType.XorJoinSplit,
            WorkflowBranchingType.AndJoinSplit,
        ]:
            handle_combined_operator(net, o)

    # for o in wf_operators:
    #     p = net.add_element(Place.create(id="LINK_WF_OPERATOR" + o.id))
    #     # split combined operator into 2 individual
    #     if o.t == WorkflowBranchingType.AndJoinXorSplit:
    #         add_wf_and_join(
    #             net=net,
    #             id="AND" + o.id,
    #             name=o.name,
    #             out_place=p,
    #             in_places=list(o.incoming_nodes),
    #         )
    #         add_wf_xor_split(
    #             net=net,
    #             id="XOR" + o.id,
    #             name=o.name,
    #             in_place=p,
    #             out_places=list(o.outgoing_nodes),
    #         )
    #     elif o.t == WorkflowBranchingType.XorJoinAndSplit:
    #         add_wf_xor_join(
    #             net=net,
    #             id="XOR" + o.id,
    #             name=o.name,
    #             out_place=p,
    #             in_places=list(o.incoming_nodes),
    #         )
    #         add_wf_and_split(
    #             net=net,
    #             id="AND" + o.id,
    #             name=o.name,
    #             in_place=p,
    #             out_places=list(o.outgoing_nodes),
    #         )
    #     else:
    #         raise Exception("invalid")
    #     # remove all original arcs and nodes from net
    #     for arc in o.all_arcs:
    #         net.remove_arc(arc)
    #     for node in o.nodes:
    #         net.remove_element(node)
