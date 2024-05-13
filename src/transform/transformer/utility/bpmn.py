from transformer.models.bpmn.bpmn import Process


def find_start_events(process: Process):
    return [se for se in process.start_events if se.get_in_degree() == 0]


def find_end_events(process: Process):
    return [ee for ee in process.end_events if ee.get_out_degree() == 0]
