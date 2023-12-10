import string
import random
import pytest

@pytest.fixture(scope="package")
def source(request):
    function_mapping = {
        "get_health": "src/health/main.py",
        "get_bpmnToPnml": "src/bpmnToPnml/main.py"
    }
    function_name = request.param
    return function_mapping[function_name]


@pytest.fixture
def random_id():
    """ Create a random ID for various purposes """
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])