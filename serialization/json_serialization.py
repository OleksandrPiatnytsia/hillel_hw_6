import json
from pathlib import Path


class JsonDataSerialization:

    DATA_FILE = Path(__file__).parent.parent / "data" / "tasks.json"

    @classmethod
    def load_tasks(cls) -> list[dict]:
        if not cls.DATA_FILE.exists():
            return []

        with open(cls.DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def save_tasks(cls, tasks: list[dict]) -> None:
        with open(cls.DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(tasks, file, ensure_ascii=False, indent=4)
