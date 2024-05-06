from xml.etree.ElementTree import Element

from lxml import etree
from pydantic_xml import BaseXmlModel

WOPED = "WoPeD"


def get_tag_name(element: Element):
    return etree.QName(element).localname.lower()


def create_silent_node_name(source: str, target: str):
    return f"SILENTFROM{source}TO{target}"


def create_arc_name(source: str | None, target: str | None):
    if source is None or target is None:
        raise Exception("source and target must have a value")
    return f"{source}TO{target}"


class BaseModel(BaseXmlModel, search_mode="unordered", skip_empty=True):
    pass
