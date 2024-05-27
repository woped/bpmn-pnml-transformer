from transform.transformer.models.bpmn.bpmn import Process
from transform.transformer.utility.bpmn import find_end_events, find_start_events


def extend_subprocess(subprocesses: set[Process], parent_process: Process):
    for subprocess in subprocesses.copy():
        #  look for start and end
        # find with zero out/in degree
        start_events = find_start_events(subprocess)
        end_events = find_end_events(subprocess)
        if not start_events or not end_events:
            raise Exception("subprocess must have atleast one start and endevent")
        start_event = start_events[0]
        end_event = end_events[0]
        #  If process has other processes -> handle recursively
        if subprocess.subprocesses:
            extend_subprocess(subprocess.subprocesses, subprocess)
        #  remove incoming/outgoing arcs and save sources/targets
        process_incoming = parent_process.get_incoming(subprocess.id).copy()
        process_outgoing = parent_process.get_outgoing(subprocess.id).copy()
        for a in [*process_incoming, *process_outgoing]:
            parent_process.remove_flow(a)
        #  remove  subprocess
        parent_process.remove_node(subprocess)
        #  add elements to parent process
        parent_process.add_nodes(*subprocess._flatten_node_typ_map())
        for flow in subprocess.flows:
            parent_process.add_constructed_flow(flow)
        #  add original arcs to start/end
        for a in process_incoming:
            parent_process.add_flow(
                parent_process.get_node(a.sourceRef), start_event, id=a.id, name=a.name
            )
        for a in process_outgoing:
            parent_process.add_flow(
                end_event, parent_process.get_node(a.targetRef), id=a.id, name=a.name
            )
