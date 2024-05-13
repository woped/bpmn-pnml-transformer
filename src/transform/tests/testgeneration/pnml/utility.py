from transformer.models.pnml.base import NetElement
from transformer.models.pnml.pnml import Pnml


def create_petri_net(test_case_name: str, flows: list[list[NetElement]]):
    net_helper = Pnml.generate_empty_net(test_case_name)
    for flow in flows:
        for element in flow:
            net_helper.net.add_element(element)
        for i in range(len(flow) - 1):
            current_node = flow[i]
            next_node = flow[i + 1]
            net_helper.net.add_arc(current_node, next_node)
    return net_helper
