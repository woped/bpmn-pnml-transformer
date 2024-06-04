"""Module to preprocess workflow event triggers.

A event trigger is a message or time.
A resource will be handled by another preprocessing function.
"""

from transformer.models.pnml.base import NetElement
from transformer.models.pnml.pnml import Net, Transition
from transformer.models.pnml.transform_helper import (
    MessageHelperPNML,
    TimeHelperPNML,
)
from transformer.utility.pnml import (
    generate_explicit_trigger_id,
)


def handle_trigger_creation(trigger: NetElement):
    """Create a trigger helper element."""
    if not trigger.toolspecific:
        raise Exception("Not possible.")
    if trigger.toolspecific.is_workflow_message():
        return MessageHelperPNML(
            id=generate_explicit_trigger_id(trigger.id), name=trigger.name
        )
    elif trigger.toolspecific.is_workflow_time():
        return TimeHelperPNML(
            id=generate_explicit_trigger_id(trigger.id), name=trigger.name
        )
    else:
        raise Exception("Should not happen.")


def handle_split(net: Net, trigger: NetElement):
    """Split into trigger helper and original element."""
    incoming_arcs = net.get_incoming_and_remove_arcs(trigger)

    explicit_trigger = handle_trigger_creation(trigger)

    net.add_element(explicit_trigger)

    net.add_arc_with_handle_same_type(explicit_trigger, trigger)

    net.connect_to_element(explicit_trigger, incoming_arcs)


def handle_join(net: Net, trigger: NetElement):
    """Split into trigger helper and original element."""
    outgoing_arcs = net.get_outgoing_and_remove_arcs(trigger)

    explicit_trigger = handle_trigger_creation(trigger)

    net.add_element(explicit_trigger)

    net.add_arc_with_handle_same_type(trigger, explicit_trigger)

    net.connect_from_element(explicit_trigger, outgoing_arcs)


def handle_join_split(net: Net, trigger: NetElement):
    """Split into trigger helper and 2 original element."""
    outgoing_arcs = net.get_outgoing_and_remove_arcs(trigger)

    explicit_trigger = handle_trigger_creation(trigger)
    and_end_gateway = Transition.create("OUTAND" + trigger.id)

    net.add_element(explicit_trigger)
    net.add_element(and_end_gateway)

    net.add_arc_with_handle_same_type(trigger, explicit_trigger)
    net.add_arc_with_handle_same_type(explicit_trigger, and_end_gateway)

    net.connect_from_element(and_end_gateway, outgoing_arcs)


def find_triggers(net: Net):
    """Find all event triggers."""
    net_elements: list[NetElement] = [*net.transitions, *net.places]
    triggers: list[NetElement] = [
        trigger for trigger in net_elements if trigger.is_workflow_event_trigger()
    ]
    return triggers


def split_event_triggers(net: Net):
    """Split the event triggers into a net and helper element."""
    triggers = find_triggers(net)
    for trigger in triggers:
        in_degree = net.get_in_degree(trigger)
        out_degree = net.get_out_degree(trigger)
        # Split and join insert trigger helper between
        if in_degree > 1 and out_degree > 1:
            handle_join_split(net, trigger)
        # Join append trigger helper
        elif in_degree > 1:
            handle_join(net, trigger)
        # Split or sequence prepend trigger helper
        elif out_degree > 1 or (in_degree == 1 and out_degree == 1):
            handle_split(net, trigger)
        else:
            raise Exception("Should not be possible")
