from flask import Flask, redirect, render_template, request, url_for

from models.clases import Task, TaskStatus
from serialization.json_serialization import JsonDataSerialization

app = Flask(__name__)


def get_tasks() -> list[Task]:
    return [Task.from_dict(item) for item in JsonDataSerialization.load_tasks()]


def save_tasks(tasks: list[Task]) -> None:
    JsonDataSerialization.save_tasks([task.to_dict() for task in tasks])


@app.route("/")
def index():
    all_tasks = get_tasks()
    stats = [
        (status, sum(1 for task in all_tasks if task.status == status))
        for status in TaskStatus
    ]
    return render_template("index.html", total=len(all_tasks), stats=stats)


@app.route("/tasks")
def tasks():
    return render_template("tasks.html", tasks=get_tasks())


@app.route("/tasks/add", methods=["GET", "POST"])
def add_task():
    error = None
    title = ""
    status = TaskStatus.new.value

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        status = request.form.get("status", TaskStatus.new.value)

        if not title:
            error = "Назва задачі не може бути порожньою"
        elif status not in [s.value for s in TaskStatus]:
            error = "Невідомий статус"
        else:
            all_tasks = get_tasks()
            new_id = max((task.id for task in all_tasks), default=0) + 1
            all_tasks.append(Task(new_id, title, TaskStatus(status)))
            save_tasks(all_tasks)
            return redirect(url_for("tasks"))

    return render_template(
        "add_task.html",
        statuses=TaskStatus,
        error=error,
        title=title,
        selected_status=status,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8000)
