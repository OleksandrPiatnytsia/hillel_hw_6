from enum import Enum


class TaskStatus(str, Enum):
    new = "new"
    in_progress = "in progress"
    done = "done"

    @property
    def label(self) -> str:
        labels = {
            TaskStatus.new: "Нова",
            TaskStatus.in_progress: "В процесі",
            TaskStatus.done: "Виконана",
        }
        return labels[self]


class Task:
    id: int
    title: str
    status: TaskStatus

    def __init__(self, id: int, title: str, status: TaskStatus = TaskStatus.new):
        self.id = id
        self.title = title
        self.status = status

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            title=data["title"],
            status=TaskStatus(data["status"]),
        )
