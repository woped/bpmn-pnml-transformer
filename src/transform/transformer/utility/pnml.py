"""Shared PNML related helper functions."""


def generate_explicit_transition_id(id: str):
    return f"EXPLICIT{id}"


def generate_source_id(id: str):
    return f"SOURCE{id}"


def generate_sink_id(id: str):
    return f"SINK{id}"
