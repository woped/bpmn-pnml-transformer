"""Extensions for unsupported nodes."""

from transformer.models.bpmn.base import NotSupportedNode


class TextAnnotation(NotSupportedNode, tag="textAnnotation"):
    """TextAnnotation extension of unsupported node."""

    pass


class ThrowEvent(NotSupportedNode, tag="intermediateThrowEvent"):
    """ThrowEvent extension of unsupported node."""

    pass


class CatchEvent(NotSupportedNode, tag="intermediateCatchEvent"):
    """CatchEvent extension of unsupported node."""

    pass
