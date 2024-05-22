"""Insert subprocess."""
from transformer.models.bpmn.base import GenericBPMNNode
from transformer.models.bpmn.bpmn import Flow, Process


def insert_temp_between_adjacent_subprocesses(bpmn: Process):
    """Add temporary subprocess elements to process."""
    subprocesses = bpmn.subprocesses
    for subprocess in subprocesses:
        out_nodes: list[tuple[GenericBPMNNode, Flow]] = [
            (bpmn.get_node(x.targetRef), x) for x in bpmn.get_outgoing(subprocess.id)
        ]

        for out_node, out_flow in out_nodes:
            if out_node not in subprocesses:
                continue
            bpmn.remove_flow(out_flow)

            linking_node = GenericBPMNNode(id=subprocess.id + out_node.id)
            bpmn.add_node(linking_node)
            bpmn.add_flow(subprocess, linking_node)
            bpmn.add_flow(linking_node, out_node)
