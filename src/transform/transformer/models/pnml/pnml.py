import os
from pathlib import Path
from typing import Optional, cast

import pm4py
from pm4py.objects.petri_net.obj import Marking
from pydantic import PrivateAttr
from pydantic_xml import attr, element

from transformer.models.pnml.base import (
    GenericNetNode,
    Graphics,
    Inscription,
    Name,
    NetElement,
    Toolspecific,
)
from transformer.utility.utility import (
    BaseModel,
    create_arc_name,
    create_silent_node_name,
)


class Transition(NetElement, tag="transition"):
    @staticmethod
    def create(id: str, name: str | None = None):
        return Transition(id=id, name=Name(title=name) if name is not None else None)


class Place(NetElement, tag="place"):
    @staticmethod
    def create(id: str, name: str | None = None):
        return Place(id=id, name=Name(title=name) if name is not None else None)


class Arc(BaseModel, tag="arc"):
    id: str = attr()
    source: str = attr()
    target: str = attr()
    inscription: Optional[Inscription] = element(default=None)
    graphics: Optional[Graphics] = element(default=None)
    toolspecific: Optional[Toolspecific] = element(default=None)

    def __hash__(self):
        return hash((type(self),) + (self.id,))


class Page(GenericNetNode, tag="page"):
    net: "Net"


class Net(BaseModel, tag="net"):
    type_field: Optional[str] = attr(default=None, alias="type")
    id: Optional[str] = attr(default=None)

    places: set[Place] = element(default_factory=set)
    transitions: set[Transition] = element(default_factory=set)
    arcs: set[Arc] = element(default_factory=set)

    pages: set[Page] = element(default_factory=set)

    # internal helper structures
    _temp_elements: dict[str, NetElement] = PrivateAttr(default_factory=dict)
    _type_map: dict[type[GenericNetNode], set[GenericNetNode]] = PrivateAttr(
        default_factory=dict
    )
    _temp_arcs: dict[str, Arc] = PrivateAttr(default_factory=dict)
    _temp_node_id_to_incoming: dict[str, set[Arc]] = PrivateAttr(default_factory=dict)
    _temp_node_id_to_outgoing: dict[str, set[Arc]] = PrivateAttr(default_factory=dict)

    def get_incoming(self, id: str):
        return self._temp_node_id_to_incoming[id]

    def get_outgoing(self, id: str):
        return self._temp_node_id_to_outgoing[id]

    def __init__(self, **data):
        super().__init__(**data)
        self._init_reference_structures()

    def _init_reference_structures(self):
        self._type_map = cast(
            dict[type[GenericNetNode], set[GenericNetNode]],
            {
                Place: self.places,
                Transition: self.transitions,
                Page: self.pages,
            },
        )
        for place in self.places:
            self._temp_elements[place.id] = place

        for transition in self.transitions:
            self._temp_elements[transition.id] = transition

        for arc in self.arcs:
            self._temp_arcs[arc.id] = arc
            self._update_arc_incoming_outgoing(arc)

    def _flatten_node_typ_map(self):
        r: list[GenericNetNode] = []
        return [r.extend(x) for x in self._type_map.values()]

    def _update_arc_incoming_outgoing(self, arc: Arc):
        if arc.target not in self._temp_node_id_to_incoming:
            self._temp_node_id_to_incoming[arc.target] = set([arc])
        else:
            self._temp_node_id_to_incoming[arc.target].add(arc)

        if arc.source not in self._temp_node_id_to_outgoing:
            self._temp_node_id_to_outgoing[arc.source] = set([arc])
        else:
            self._temp_node_id_to_outgoing[arc.source].add(arc)

    def get_in_degree(self, node: GenericNetNode):
        if node.id not in self._temp_node_id_to_incoming:
            return 0
        return len(self._temp_node_id_to_incoming[node.id])

    def get_out_degree(self, node: GenericNetNode):
        if node.id not in self._temp_node_id_to_outgoing:
            return 0
        return len(self._temp_node_id_to_outgoing[node.id])

    def add_arc_with_handle_same_type_from_id(self, source_id: str, target_id: str):
        source = self._temp_elements[source_id]
        target = self._temp_elements[target_id]
        self.add_arc_with_handle_same_type(source, target)

    def add_arc_with_handle_same_type(self, source: NetElement, target: NetElement):
        if isinstance(source, Place) and isinstance(target, Place):
            t = self.add_element(
                Transition(id=create_silent_node_name(source.id, target.id))
            )
            self.add_arc(source, t)
            self.add_arc(t, target)
        elif isinstance(source, Transition) and isinstance(target, Transition):
            p = self.add_element(
                Place(id=create_silent_node_name(source.id, target.id))
            )
            self.add_arc(source, p)
            self.add_arc(p, target)
        else:
            self.add_arc(source, target)

    def add_arc(self, source: NetElement, target: NetElement, id: str | None = None):
        if id is None:
            id = create_arc_name(source.id, target.id)
        if type(source) is type(target):
            raise Exception("Cant connect identical petrinet elements")
        if id in self._temp_arcs:
            raise Exception(f"arc {id} already exists from {source.id} to {target.id}!")

        self.add_element(source)
        self.add_element(target)

        a = Arc(id=id, source=source.id, target=target.id)
        self._temp_arcs[id] = a
        self._update_arc_incoming_outgoing(a)

        self.arcs.add(a)

    def remove_arc(self, arc: Arc):
        arc_id = arc.id
        self._temp_arcs.pop(arc_id)
        if arc.target:
            self._temp_node_id_to_incoming[arc.target].remove(arc)
        if arc.source:
            self._temp_node_id_to_outgoing[arc.source].remove(arc)

        self.arcs.remove(arc)

    def add_page(self, new_page: Page):
        storage_set = self.pages
        for p in self.pages:
            if p.id == new_page.id:
                return p

        storage_set.add(new_page)
        return new_page

    def add_element(self, new_node: NetElement):
        storage_set = self._type_map[type(new_node)]
        if storage_set is None:
            raise Exception("No Petrinet node")

        if new_node.id in self._temp_elements:
            return new_node

        storage_set.add(new_node)

        self._temp_elements[new_node.id] = new_node
        return new_node

    def get_element(self, id: str):
        if id not in self._temp_elements:
            raise Exception("Cant get nonexisting Node")
        return self._temp_elements[id]

    def get_page(self, id: str):
        pages = {p.id: p for p in self.pages}
        if id not in pages:
            raise Exception("Cant find page")
        return pages[id]

    def get_node_or_none(self, id: str):
        if id not in self._temp_elements:
            return None
        return self._temp_elements[id]

    def remove_element(self, to_remove_node: GenericNetNode):
        storage_set = self._type_map[type(to_remove_node)]
        if storage_set is None:
            raise Exception("No Petrinet node")

        storage_set.remove(to_remove_node)

        self._temp_elements.pop(to_remove_node.id)
        incoming = self._temp_node_id_to_incoming.pop(to_remove_node.id)
        outgoing = self._temp_node_id_to_outgoing.pop(to_remove_node.id)
        for arc in incoming:
            arc.target = ""
        for arc in outgoing:
            arc.source = ""


# Page is using Net reference before Net is initalized
Page.model_rebuild()


class Pnml(BaseModel, tag="pnml"):
    net: Net

    def to_string(self) -> str:
        return cast(str, self.to_xml(encoding="unicode", pretty_print=True))

    def write_to_file(self, path: str):
        Path(path).write_text(self.to_string())

    def to_pm4py_vis(self, file_path: str):
        TEMP_FILE = "temp.pnml"
        self.write_to_file(TEMP_FILE)
        net = pm4py.read_pnml(TEMP_FILE)[0]
        pm4py.save_vis_petri_net(net, Marking(), Marking(), file_path)
        os.remove(TEMP_FILE)

    @staticmethod
    def from_xml_str(xml_content: str):
        net = Pnml.from_xml(bytes(xml_content, encoding="utf-8"))
        return net

    @staticmethod
    def from_file(path: str):
        return Pnml.from_xml_str(Path(path).read_text())

    @staticmethod
    def generate_empty_net(id="new_net"):
        return Pnml(net=Net(id=id))
