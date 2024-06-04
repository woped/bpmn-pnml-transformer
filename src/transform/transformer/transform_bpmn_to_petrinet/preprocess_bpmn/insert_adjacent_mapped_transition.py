"""Insert GenericBPMNNodes."""

from transformer.models.bpmn.base import Gateway, GenericBPMNNode
from transformer.models.bpmn.bpmn import Flow, Process


def is_target_wf_transition(node):
    """If node will be transformed to transition."""
    return isinstance(node, Process | Gateway)


def insert_temp_between_adjacent_mapped_transition(bpmn: Process):
    """Add helper Nodes.

    Adjacent BPMN Elements that will be transformed to transitions will break
    workflow elements.
    As a solution GenericBPMNNodes are inserted between them.
    They will be transformed to Places as part of the transformation.
    """
    nodes = bpmn._flatten_node_typ_map()
    for node in nodes:
        if not is_target_wf_transition(node):
            continue

        out_nodes: list[tuple[GenericBPMNNode, Flow]] = [
            (bpmn.get_node(x.targetRef), x) for x in bpmn.get_outgoing(node.id)
        ]

        for out_node, out_flow in out_nodes:
            if not is_target_wf_transition(out_node):
                continue
            bpmn.remove_flow(out_flow)

            linking_node = GenericBPMNNode(id=node.id + out_node.id)
            bpmn.add_node(linking_node)
            bpmn.add_flow(node, linking_node)
            bpmn.add_flow(linking_node, out_node)
