"""Shared PNML related helper functions."""


def generate_explicit_transition_id(id: str):
    """Prepend EXPLICIT to the id."""
    return f"EXPLICIT{id}"


def generate_explicit_trigger_id(id: str):
    """Prepend EXPLICIT to the id."""
    return f"TRIGGER{id}"


def generate_source_id(id: str):
    """Prepend SOURCE to the id."""
    return f"SOURCE{id}"


def generate_sink_id(id: str):
    """Prepend SINK to the id."""
    return f"SINK{id}"
