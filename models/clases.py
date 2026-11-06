from datetime import datetime
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
    created_at: datetime | None

    def __init__(
        self,
        id: int,
        title: str,
        status: TaskStatus = TaskStatus.new,
        created_at: datetime | None = None,
    ):
        self.id = id
        self.title = title
        self.status = status
        self.created_at = created_at

    @property
    def created_at_display(self) -> str:
        if self.created_at is None:
            return "—"
        return self.created_at.strftime("%d.%m.%Y %H:%M")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(timespec="seconds") if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        created_at = data.get("created_at")  # у старих задачах цього поля може не бути
        return cls(
            id=data["id"],
            title=data["title"],
            status=TaskStatus(data["status"]),
            created_at=datetime.fromisoformat(created_at) if created_at else None,
        )
