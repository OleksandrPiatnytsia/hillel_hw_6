from flask import Flask, abort, redirect, render_template, request, url_for

from models.clases import Task, TaskStatus
from serialization.json_serialization import JsonDataSerialization

app = Flask(__name__)

TASKS_PER_PAGE = 9


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
    all_tasks = get_tasks()
    total_pages = max(1, -(-len(all_tasks) // TASKS_PER_PAGE))  # ділення з округленням вгору

    page = request.args.get("page", 1, type=int)
    page = min(max(page, 1), total_pages)

    start = (page - 1) * TASKS_PER_PAGE
    page_tasks = all_tasks[start:start + TASKS_PER_PAGE]

    return render_template(
        "tasks.html",
        tasks=page_tasks,
        total=len(all_tasks),
        page=page,
        total_pages=total_pages,
    )


@app.route("/tasks/<int:task_id>")
def task_detail(task_id: int):
    all_tasks = get_tasks()

    for position, task in enumerate(all_tasks):
        if task.id == task_id:
            # сторінка списку, на якій знаходиться ця задача (для кнопки "Назад")
            page = position // TASKS_PER_PAGE + 1
            return render_template("task_detail.html", task=task, page=page)

    abort(404)


def validate_task_form(title: str, status: str) -> str | None:
    """Повертає текст помилки або None, якщо дані форми коректні."""
    if not title:
        return "Назва задачі не може бути порожньою"
    if status not in [s.value for s in TaskStatus]:
        return "Невідомий статус"
    return None


@app.route("/tasks/add", methods=["GET", "POST"])
def add_task():
    error = None
    title = ""
    status = TaskStatus.new.value

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        status = request.form.get("status", TaskStatus.new.value)
        error = validate_task_form(title, status)

        if error is None:
            all_tasks = get_tasks()
            new_id = max((task.id for task in all_tasks), default=0) + 1
            all_tasks.append(Task(new_id, title, TaskStatus(status)))
            save_tasks(all_tasks)
            last_page = -(-len(all_tasks) // TASKS_PER_PAGE)
            return redirect(url_for("tasks", page=last_page))

    return render_template(
        "task_form.html",
        heading="Нова задача",
        action_url=url_for("add_task"),
        cancel_url=url_for("tasks"),
        statuses=TaskStatus,
        error=error,
        title=title,
        selected_status=status,
    )


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id: int):
    all_tasks = get_tasks()
    task = next((t for t in all_tasks if t.id == task_id), None)
    if task is None:
        abort(404)

    error = None
    title = task.title
    status = task.status.value

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        status = request.form.get("status", task.status.value)
        error = validate_task_form(title, status)

        if error is None:
            task.title = title
            task.status = TaskStatus(status)
            save_tasks(all_tasks)
            return redirect(url_for("task_detail", task_id=task.id))

    return render_template(
        "task_form.html",
        heading=f"Редагування задачі #{task.id}",
        action_url=url_for("edit_task", task_id=task.id),
        cancel_url=url_for("task_detail", task_id=task.id),
        statuses=TaskStatus,
        error=error,
        title=title,
        selected_status=status,
    )


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id: int):
    all_tasks = get_tasks()
    position = next((i for i, t in enumerate(all_tasks) if t.id == task_id), None)
    if position is None:
        abort(404)

    all_tasks.pop(position)
    save_tasks(all_tasks)

    # повертаємось на ту сторінку списку, де була задача
    # (якщо після видалення вона спорожніла, /tasks сам перекине на останню)
    page = position // TASKS_PER_PAGE + 1
    return redirect(url_for("tasks", page=page))


if __name__ == "__main__":
    app.run(debug=True, port=8000)
