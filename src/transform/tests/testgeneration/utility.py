import shutil
from pathlib import Path

OUT_PATH = "out"


def set_out_path(path: str):
    global OUT_PATH
    OUT_PATH = path


def clear():
    try:
        shutil.rmtree(OUT_PATH)
    except Exception:
        pass


def create_file_path(file_name: str, test_case_name: str):
    Path(f"{OUT_PATH}/{test_case_name}").mkdir(parents=True, exist_ok=True)
    return f"{OUT_PATH}/{test_case_name}/{file_name}"


def read_bpmn_file(case_name: str):
    return Path(f"{OUT_PATH}/{case_name}/bpmn.bpmn").read_text()


class UniqueIDGenerator:
    running_id = 0

    @staticmethod
    def generate() -> str:
        UniqueIDGenerator.running_id += 1
        return f"element_{UniqueIDGenerator.running_id}"
