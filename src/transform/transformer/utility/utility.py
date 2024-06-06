"""General transformer utility (get name, create basic elements/nodes)."""

from xml.etree.ElementTree import Element

from lxml import etree
from pydantic_xml import BaseXmlModel

WOPED = "WoPeD"


def get_tag_name(element: Element):
    """Return the lowercase tag name of an element."""
    return etree.QName(element).localname.lower()


def create_silent_node_name(source: str, target: str):
    """Construct a silent node (name) from source to target."""
    return f"SILENTFROM{source}TO{target}"


def create_arc_name(source: str | None, target: str | None):
    """Construct an arc (name) from source to target."""
    if source is None or target is None:
        raise Exception("source and target must have a value")
    return f"{source}TO{target}"


class BaseModel(
    BaseXmlModel,
    search_mode="unordered",
    skip_empty=True,
):
    """BaseModel extension of BaseXmlModel."""


class BaseBPMNModel(
    BaseXmlModel,
    search_mode="unordered",
    skip_empty=True,
    nsmap={"": "http://www.omg.org/spec/BPMN/20100524/MODEL"},
):
    """BaseBPMNModel extension of BaseXmlModel."""
