from enum import Enum


class TaskStatus(str, Enum):
    new = "new"
    in_progres = "in progres"
    done = "done"


class Task:
    title: str
    status: TaskStatus

    def __init__(self, title: str, status: TaskStatus):
        self.title = title
        self.status = status
