from transformer.models.bpmn.base import NotSupportedNode


class TextAnnotation(NotSupportedNode, tag="textAnnotation"):
    pass


class ThrowEvent(NotSupportedNode, tag="intermediateThrowEvent"):
    pass


class CatchEvent(NotSupportedNode, tag="intermediateCatchEvent"):
    pass
