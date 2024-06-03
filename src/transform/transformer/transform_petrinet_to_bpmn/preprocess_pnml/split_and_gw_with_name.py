"""Split a AND transition with a name (implicit task)."""

from transformer.models.pnml.base import NetElement
from transformer.models.pnml.pnml import Arc, Net, Transition
from transformer.utility.pnml import generate_explicit_transition_id


def get_incoming_and_remove_arcs(net: Net, transition: Transition):
    incoming_arcs = [arc.model_copy() for arc in net.get_incoming(transition.id)]
    for to_remove_arc in incoming_arcs:
        net.remove_arc(to_remove_arc)
    return incoming_arcs


def get_outgoing_and_remove_arcs(net: Net, transition: Transition):
    outgoing_arcs = [arc.model_copy() for arc in net.get_outgoing(transition.id)]
    for to_remove_arc in outgoing_arcs:
        net.remove_arc(to_remove_arc)
    return outgoing_arcs


def get_incoming_outgoing_and_remove_arcs(net: Net, transition: Transition):
    return get_incoming_and_remove_arcs(net, transition), get_outgoing_and_remove_arcs(
        net, transition
    )


def connect_to_element(net: Net, element: NetElement, incoming_arcs: list[Arc]):
    for arc in incoming_arcs:
        net.add_arc_from_id(arc.source, element.id)


def connect_from_element(net: Net, element: NetElement, outgoing_arcs: list[Arc]):
    for arc in outgoing_arcs:
        net.add_arc_from_id(element.id, arc.target)


def handle_split(net: Net, and_gateway: Transition):
    incoming_arcs = get_incoming_and_remove_arcs(net, and_gateway)

    explicit_transition = Transition.create(
        generate_explicit_transition_id(and_gateway.id), and_gateway.get_name()
    )

    net.add_element(explicit_transition)

    net.add_arc_with_handle_same_type(explicit_transition, and_gateway)

    connect_to_element(net, explicit_transition, incoming_arcs)


def handle_join(net: Net, and_gateway: Transition):
    outgoing_arcs = get_outgoing_and_remove_arcs(net, and_gateway)

    explicit_transition = Transition.create(
        generate_explicit_transition_id(and_gateway.id), and_gateway.get_name()
    )

    net.add_element(explicit_transition)

    net.add_arc_with_handle_same_type(and_gateway, explicit_transition)

    connect_from_element(net, explicit_transition, outgoing_arcs)


def handle_join_split(net: Net, and_gateway: Transition):
    outgoing_arcs = get_outgoing_and_remove_arcs(net, and_gateway)

    explicit_transition = Transition.create(
        generate_explicit_transition_id(and_gateway.id), and_gateway.get_name()
    )
    and_end_gateway = Transition.create("OUTAND" + and_gateway.id)

    net.add_element(explicit_transition)
    net.add_element(and_end_gateway)

    net.add_arc_with_handle_same_type(and_gateway, explicit_transition)
    net.add_arc_with_handle_same_type(explicit_transition, and_end_gateway)

    connect_from_element(net, and_end_gateway, outgoing_arcs)


def split_and_gw_with_name(net: Net):
    and_gateways = [
        t
        for t in net.transitions
        if net.get_in_degree(t) > 1 or net.get_out_degree(t) > 1 and t.get_name()
    ]
    for and_gateway in and_gateways:
        in_degree = net.get_in_degree(and_gateway)
        out_degree = net.get_out_degree(and_gateway)
        # Split and join
        if in_degree > 1 and out_degree > 1:
            handle_join_split(net, and_gateway)
        # Join
        elif in_degree > 1:
            handle_join(net, and_gateway)
        # Split
        elif out_degree > 1:
            handle_split(net, and_gateway)
        else:
            raise Exception("Should not be possible")

        # Remove name because already handled by explicit transition
        and_gateway.name = None
