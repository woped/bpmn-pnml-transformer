"""Pytest shared config.

This module contains fixtures and utilities for testing.
"""

import string
import random
import pytest


def pytest_itemcollected(item):
    """Modifies pytest test names using class and method docstrings.

    Alters the pytest item's nodeid by combining the parent class and test 
    method docstrings, defaulting to their names if docstrings are absent.

    Args:
        item: The pytest test item to modify.
    """

@pytest.fixture(scope="package")
def source(request):
    """Provides the file path mapping for a given function name.

    Args:
        request (FixtureRequest): A request object giving access to the
                                  requesting test context.

    Returns:
        str: The file path of the specified function.

    Raises:
        KeyError: If the function name is not in the mapping.
    """
    function_mapping = {
        "get_health": "src/health/main.py",
        "get_bpmnToPnml": "src/bpmnToPnml/main.py"
    }
    function_name = request.param
    return function_mapping[function_name]


@pytest.fixture
def random_id():
    """Generates a random alphanumeric ID of fixed length.

    This fixture creates a 10-character long random ID, using a combination of
    uppercase and lowercase ASCII letters. It is used for generating unique
    identifiers for test cases.

    Returns:
        str: A 10-character random alphanumeric ID.
    """
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])
