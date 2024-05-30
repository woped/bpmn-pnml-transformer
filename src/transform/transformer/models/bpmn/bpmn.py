"""BPMN objects and handling."""

from pathlib import Path
from typing import cast
from xml.etree.ElementTree import Element

from lxml import etree, objectify
from pydantic import PrivateAttr
from pydantic_xml import attr, element

from transformer.exceptions import NotSupportedBPMNElement
from transformer.models.bpmn.base import (
    BPMNNamespace,
    Gateway,
    GenericBPMNNode,
    GenericIdNode,
)
from transformer.models.bpmn.bpmn_graphics import (
    BPMNDiagram,
    BPMNEdge,
    BPMNLabel,
    BPMNPlane,
    BPMNShape,
    DCBounds,
    DIWaypoint,
)
from transformer.models.bpmn.not_supported_models import CatchEvent, ThrowEvent
from transformer.utility.utility import create_arc_name, get_tag_name

not_supported_elements = {
    # custom element
    "extensionelements",
    # gateways
    "complexgateway",
    "eventbasedgateway",
    # tasks
    "usertask",
    "servicetask",
    "sendtask",
    "receivetask",
    "manualtask",
    "businessruletask",
    "scripttask",
    "callactivity",
    # events
    # https://www.omg.org/spec/BPMN/2.0/PDF P. 425
    "intermediatethrowevent",
    "normalintermediatethrowevent",
    "intermediatecatchevent",
    "boundaryevent",
}


# Gateways
class XorGateway(Gateway, tag="exclusiveGateway"):
    """XOR extension of gateways."""

    pass


class AndGateway(Gateway, tag="parallelGateway"):
    """AND extension of gateways."""

    pass


class OrGateway(Gateway, tag="inclusiveGateway"):
    """OR extension of gateways."""

    pass


# Events
class StartEvent(GenericBPMNNode, tag="startEvent"):
    """StartEvent extension of GenericBPMNNode."""

    pass


class EndEvent(GenericBPMNNode, tag="endEvent"):
    """EndEvent extension of GenericBPMNNode."""

    pass


#
class Flow(GenericIdNode, tag="sequenceFlow"):
    """Flow extension of GenericBPMNNode."""

    name: str | None = attr(default=None)
    sourceRef: str = attr()
    targetRef: str = attr()


class Task(GenericBPMNNode, tag="task"):
    """Task extension of GenericBPMNNode."""

    pass


class Process(GenericBPMNNode):
    """Process extension of GenericBPMNNode."""

    isExecutable: bool | None = attr(default=None)

    start_events: set[StartEvent] = element(default_factory=set)

    tasks: set[Task] = element(default_factory=set)
    end_events: set[EndEvent] = element(default_factory=set)

    xor_gws: set[XorGateway] = element(default_factory=set)
    or_gws: set[OrGateway] = element(default_factory=set)
    and_gws: set[AndGateway] = element(default_factory=set)

    subprocesses: set["Process"] = element(default_factory=set, tag="subProcess")

    flows: set[Flow] = element(default_factory=set)

    not_supported: list[ThrowEvent | CatchEvent] = element(default_factory=list)

    # internal helper structures
    _type_map: dict[type[GenericBPMNNode], set[GenericBPMNNode]] = PrivateAttr(
        default_factory=dict
    )

    _temp_node_id_to_incoming: dict[str, set[Flow]] = PrivateAttr(default_factory=dict)
    _temp_node_id_to_outgoing: dict[str, set[Flow]] = PrivateAttr(default_factory=dict)
    _temp_nodes: dict[str, GenericBPMNNode] = PrivateAttr(default_factory=dict)
    _temp_flows: dict[str, Flow] = PrivateAttr(default_factory=dict)

    def __init__(self, **data):
        """Process instance constructor."""
        super().__init__(**data)
        self._init_reference_structures()

    def _init_reference_structures(self):
        """Instance initializer."""
        self._type_map = cast(
            dict[type[GenericBPMNNode], set[GenericBPMNNode]],
            {
                Task: self.tasks,
                StartEvent: self.start_events,
                EndEvent: self.end_events,
                XorGateway: self.xor_gws,
                OrGateway: self.or_gws,
                AndGateway: self.and_gws,
                Process: self.subprocesses,
                GenericBPMNNode: set(),
            },
        )
        self._temp_node_id_to_incoming: dict[str, set[Flow]] = {}
        self._temp_node_id_to_outgoing: dict[str, set[Flow]] = {}
        self._temp_nodes: dict[str, GenericBPMNNode] = {}
        self._temp_flows: dict[str, Flow] = {}

        for node in self._flatten_node_typ_map():
            self._temp_nodes[node.id] = node

        for flow in self.flows:
            self._temp_flows[flow.id] = flow
            self._update_flow_incoming_outgoing(flow)

    def _flatten_node_typ_map(self):
        """Flatten nodes."""
        r: list[GenericBPMNNode] = []
        [r.extend(x) for x in self._type_map.values()]
        return r

    def _update_flow_incoming_outgoing(self, flow: Flow):
        """Update source / target reference of instance."""
        if flow.targetRef not in self._temp_node_id_to_incoming:
            self._temp_node_id_to_incoming[flow.targetRef] = set([flow])
        else:
            self._temp_node_id_to_incoming[flow.targetRef].add(flow)

        if flow.sourceRef not in self._temp_node_id_to_outgoing:
            self._temp_node_id_to_outgoing[flow.sourceRef] = set([flow])
        else:
            self._temp_node_id_to_outgoing[flow.sourceRef].add(flow)

    def _update_actual_incoming_outgoing(self, flow: Flow):
        """Update underlying source / target of instance."""
        self.flows.add(flow)
        source = self._temp_nodes[flow.sourceRef]
        target = self._temp_nodes[flow.targetRef]
        source.outgoing.add(flow.id)
        target.incoming.add(flow.id)

    def get_incoming(self, id: str):
        """Return the incoming flows of a element by id."""
        return self._temp_node_id_to_incoming[id]

    def get_outgoing(self, id: str):
        """Return the outgoing flows of a element by id."""
        return self._temp_node_id_to_outgoing[id]

    def get_node(self, id: str):
        """Return a node by id."""
        return self._temp_nodes[id]

    def change_node_id(self, node: GenericBPMNNode, new_id: str):
        """Change node id and update connected flows."""
        incoming_flows = self._temp_node_id_to_incoming.get(node.id, [])
        incoming_flows_id_map = [
            (f.id, f.sourceRef, new_id, f.name) for f in incoming_flows
        ]

        outgoing_flows = self._temp_node_id_to_outgoing.get(node.id, [])
        outgoing_flows_id_map = [
            (f.id, new_id, f.targetRef, f.name) for f in outgoing_flows
        ]

        for f in [*incoming_flows, *outgoing_flows]:
            self.remove_flow(f)
        self.remove_node(node)

        new_node = node.model_copy(deep=True)
        new_node.id = new_id

        self.add_node(new_node)
        for id, source_id, target_id, name in [
            *outgoing_flows_id_map,
            *incoming_flows_id_map,
        ]:
            self.add_flow(
                source=self._temp_nodes[source_id],
                target=self._temp_nodes[target_id],
                id=id,
                name=name,
            )

    def add_flow(
        self,
        source: GenericBPMNNode,
        target: GenericBPMNNode,
        id: str | None = None,
        name: str | None = None,
    ):
        """Add flow to instance by source and target."""
        if id is None:
            id = create_arc_name(source.id, target.id)

        if id in self._temp_flows:
            raise Exception(f"flow with the id {id} already exists!")

        self.add_node(source)
        self.add_node(target)

        a = Flow(id=id, sourceRef=source.id, targetRef=target.id, name=name)
        self._temp_flows[id] = a
        self._update_flow_incoming_outgoing(a)
        self._update_actual_incoming_outgoing(a)
        return a

    def add_constructed_flow(self, flow: Flow):
        """Add a finished flow to instance."""
        self.add_flow(
            self._temp_nodes[flow.sourceRef],
            self._temp_nodes[flow.targetRef],
            flow.id,
            flow.name,
        )

    def _remove_actual_flow(self, flow: Flow):
        """Remove underlying flow of instance."""
        self.flows.remove(flow)

        source = self._temp_nodes[flow.sourceRef]
        target = self._temp_nodes[flow.targetRef]
        source.outgoing.remove(flow.id)
        target.incoming.remove(flow.id)

    def remove_flow(self, flow: Flow):
        """Remove flow reference of instance."""
        self._temp_flows.pop(flow.id)
        self._temp_node_id_to_incoming[flow.targetRef].remove(flow)
        self._temp_node_id_to_outgoing[flow.sourceRef].remove(flow)

        self._remove_actual_flow(flow)

    def add_nodes(self, *args: GenericBPMNNode):
        """Add multiple nodes to the BPMN."""
        for node in args:
            self.add_node(node)

    def add_node(self, new_node: GenericBPMNNode):
        """Add single node to the BPMN."""
        storage_set = self._type_map[type(new_node)]
        if storage_set is None:
            raise Exception("No BPMN node")
        if new_node in storage_set:
            # skip already added node
            return new_node

        storage_set.add(new_node)

        self._temp_nodes[new_node.id] = new_node

        return new_node

    def remove_node(self, to_remove_node: GenericBPMNNode):
        """Remove single node frome the BPMN."""
        storage_set = self._type_map[type(to_remove_node)]
        if storage_set is None:
            raise Exception("No BPMN node")

        if to_remove_node not in storage_set:
            raise Exception("Node doesnt exist")

        storage_set.remove(to_remove_node)

        self._temp_nodes.pop(to_remove_node.id)

        if to_remove_node.id in self._temp_node_id_to_incoming:
            incoming = self._temp_node_id_to_incoming.pop(to_remove_node.id)
            for arc in incoming:
                arc.targetRef = ""
        if to_remove_node.id in self._temp_node_id_to_outgoing:
            outgoing = self._temp_node_id_to_outgoing.pop(to_remove_node.id)
            for arc in outgoing:
                arc.sourceRef = ""

    def get_flow_target_by_id(self, flow_id: str):
        """Return target nodes from flow id."""
        return self._temp_nodes[self._temp_flows[flow_id].targetRef]

    def get_flow_source_by_id(self, flow_id: str):
        """Return source nodes from flow id."""
        return self._temp_nodes[self._temp_flows[flow_id].sourceRef]

    def get_flow(self, id: str):
        """Return flow by id."""
        return self._temp_flows[id]

    def remove_node_with_connecting_flows(self, node: GenericBPMNNode):
        """Remove node and its connected flows."""
        if node.get_in_degree() > 0:
            incoming_arc = list(self._temp_node_id_to_incoming[node.id])[0]
            source_id = incoming_arc.sourceRef
            self.remove_flow(incoming_arc)
        if node.get_out_degree() > 0:
            outgoing_arc = list(self._temp_node_id_to_outgoing[node.id])[0]
            target_id = outgoing_arc.targetRef
            self.remove_flow(outgoing_arc)
        self.remove_node(node)
        return source_id, target_id


class BPMN(BPMNNamespace, tag="definitions"):
    """Extension of BPMNNamespace with attributes process and diagram."""

    process: Process = element(tag="process")
    diagram: BPMNDiagram | None = element(default=None)

    @staticmethod
    def from_xml(xml_content: str):
        """Return a BPMN from a XML string."""
        parser = etree.XMLParser()
        tree: Element = objectify.fromstring(
            bytes(xml_content, encoding="utf-8"), parser
        )
        used_tags: set[str] = set()
        for elem in tree.iter():
            used_tags.add(get_tag_name(elem))
        shared_tags = used_tags.intersection(not_supported_elements)
        if len(shared_tags) > 0:
            raise NotSupportedBPMNElement(
                "The following tags are not supported: ", shared_tags
            )
        return BPMN.from_xml_tree(tree)

    @staticmethod
    def from_file(path: str):
        """Return a BPMN from a file path."""
        content = Path(path).read_text()
        return BPMN.from_xml(content)

    @staticmethod
    def generate_empty_bpmn(id="new_bpmn"):
        """Return an empty bpmn with a process."""
        return BPMN(process=Process(id=id, isExecutable=True))

    def to_string(self) -> str:
        """Transform this instance into a string and creates placeholder graphics."""
        self.set_graphics()
        return cast(str, self.to_xml(encoding="unicode", pretty_print=False))

    def write_to_file(self, path: str):
        """Save this instance xml encoded to a file."""
        content = self.to_string()
        Path(path).write_text(content)

    def set_graphics(self):
        """Define graphical representation of this instance."""
        d = BPMNDiagram(id="diagram1")
        bpmn = self.process
        p = BPMNPlane(id=f"plane{bpmn.id}", bpmnElement=bpmn.id)
        for flow in bpmn.flows:
            p.eles.append(
                BPMNEdge(
                    id=f"{flow.id}_di",
                    bpmnElement=flow.id,
                    waypoints=[DIWaypoint(), DIWaypoint()],
                )
            )

        for node in bpmn._flatten_node_typ_map():
            s = BPMNShape(
                id=f"{node.id}_di",
                bpmnElement=node.id,
                bounds=DCBounds(width=100, height=80),
            )
            if isinstance(node, Process):
                s.isExpanded = True
            if node.name and not isinstance(node, Process | Task):
                s.label = BPMNLabel(bounds=DCBounds(width=50, height=20))
            p.eles.append(s)

        d.plane = p
        self.diagram = d
