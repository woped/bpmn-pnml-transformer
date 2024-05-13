import io
from typing import Any
from xml.dom import minidom

from transformer.models.bpmn.base import GenericBPMNNode
from transformer.models.bpmn.bpmn import BPMN, Flow
from transformer.utility.utility import create_arc_name


def create_bpmn(test_case_name: str, flows: list[list[GenericBPMNNode]]):
    bpmn = BPMN.generate_empty_bpmn(test_case_name)
    all_flows = []
    for flow in flows:
        all_flows.extend(create_flows(bpmn, flow))
    for flow in all_flows:
        bpmn.process.add_constructed_flow(flow)
    return bpmn


def create_flows(
    bpmn_in: BPMN, row: list[GenericBPMNNode], arc_label: dict[Any, str] | None = None
) -> list[Flow]:
    bpmn = bpmn_in.process
    if not arc_label:
        arc_label = {}
    flows: list[Flow] = []
    for i in range(0, len(row) - 1):
        source = row[i]
        target = row[i + 1]
        label = arc_label.get(source, None)
        id = create_arc_name(source.id, target.id)

        bpmn.add_node(source)
        bpmn.add_node(target)

        flows.append(Flow(sourceRef=source.id, targetRef=target.id, id=id, name=label))
    return flows


def rename_bpmn_xml(xml_content: str, new_tag: str):
    dom = minidom.parseString(xml_content)
    hit = dom.getElementsByTagName("bpmn:task")[0]
    hit.tagName = new_tag
    f = io.StringIO()
    dom.writexml(f)
    val = f.getvalue()
    f.close()
    return val


def insert_bpmn_xml(xml_content: str, new_tag: str, force_id: str = "temp"):
    dom = minidom.parseString(xml_content)
    process_tag = dom.getElementsByTagName("bpmn:process")
    hit = process_tag[0]
    hit.setAttribute("id", force_id)
    hit.appendChild(minidom.Element(new_tag))
    f = io.StringIO()
    dom.writexml(f)
    val = f.getvalue()
    f.close()
    return val
