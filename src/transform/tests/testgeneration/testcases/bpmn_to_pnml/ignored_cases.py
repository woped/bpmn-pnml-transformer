import shutil

from testgeneration.bpmn.utility import create_bpmn, insert_bpmn_xml
from testgeneration.pnml.utility import create_petri_net
from testgeneration.utility import UniqueIDGenerator, create_file_path, read_bpmn_file

from transform.transformer.models.bpmn.bpmn import EndEvent, StartEvent, Task
from transform.transformer.models.pnml.pnml import Place, Pnml, Transition


def generate_helper_bpmn(case_name: str):
    se_id = "elem_1"
    ee_id = "elem_2"
    task_id = "elem_3"
    bpmn = create_bpmn(
        case_name, [[StartEvent(id=se_id), Task(id=task_id), EndEvent(id=ee_id)]]
    )
    bpmn.write_to_file(create_file_path("bpmn.bpmn", case_name))
    return read_bpmn_file(case_name)


def generate_temp_petri_net(case_name: str):
    se_id = "elem_1"
    ee_id = "elem_2"
    task_id = "elem_3"
    return create_petri_net(
        case_name, [[Place(id=se_id), Transition(id=task_id), Place(id=ee_id)]]
    )


def generate():
    temp_case_name = UniqueIDGenerator.generate()
    bpmn = generate_helper_bpmn(temp_case_name)
    pn = generate_temp_petri_net(temp_case_name)
    items: list[tuple[str, Pnml]] = []
    for case_name in [
        "collaboration",
        "laneSet",
        "dataStoreReference",
        "dataObjectReference",
        "dataObject",
        "category",
        "textAnnotation",
    ]:
        r = insert_bpmn_xml(bpmn, f"bpmn:{case_name}", temp_case_name)
        items.append((r, pn))
    shutil.rmtree(create_file_path("", temp_case_name).rsplit("/", 1)[0])
    return items


all_cases = generate()
