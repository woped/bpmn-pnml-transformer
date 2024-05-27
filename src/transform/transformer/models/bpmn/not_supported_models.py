from transform.transformer.models.bpmn.base import NotSupportedNode


class TextAnnotation(NotSupportedNode, tag="textAnnotation"):
    """TextAnnotation extension of unsupported node."""
    pass


class ThrowEvent(NotSupportedNode, tag="intermediateThrowEvent"):
    """Throw extension of unsupported node."""
    pass


class CatchEvent(NotSupportedNode, tag="intermediateCatchEvent"):
    """Catch extension of unsupported node."""
    pass
