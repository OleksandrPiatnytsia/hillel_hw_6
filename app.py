from datetime import datetime

from flask import Flask, abort, redirect, render_template, request, url_for

from models.clases import Task, TaskStatus
from serialization.json_serialization import JsonDataSerialization

app = Flask(__name__)

TASKS_PER_PAGE = 9

DEFAULT_SORT = "newest"
SORT_OPTIONS = {
    "newest": "Спочатку нові",
    "oldest": "Спочатку старі",
}


def get_tasks() -> list[Task]:
    return [Task.from_dict(item) for item in JsonDataSerialization.load_tasks()]


def save_tasks(tasks: list[Task]) -> None:
    JsonDataSerialization.save_tasks([task.to_dict() for task in tasks])


def get_list_args() -> dict:
    """
    Параметри списку задач з адреси (?status=...&sort=...&page=...).
    Повертає лише коректні значення і не включає значення за замовчуванням,
    щоб адреси лишались короткими. Їх передаємо між сторінками,
    щоб після перегляду/редагування/видалення повернутись у той самий список.
    """
    args = {}

    status = request.args.get("status")
    if status in [s.value for s in TaskStatus]:
        args["status"] = status

    sort = request.args.get("sort")
    if sort in SORT_OPTIONS and sort != DEFAULT_SORT:
        args["sort"] = sort

    page = request.args.get("page", type=int)
    if page and page > 1:
        args["page"] = page

    return args


def sort_tasks(tasks: list[Task], sort: str) -> list[Task]:
    # задачі без дати вважаємо найстарішими; при однаковій даті сортуємо за id
    return sorted(
        tasks,
        key=lambda t: (t.created_at or datetime.min, t.id),
        reverse=(sort == "newest"),
    )


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
    args = get_list_args()
    status = args.get("status")
    sort = args.get("sort", DEFAULT_SORT)

    all_tasks = get_tasks()
    counts = {s.value: sum(1 for t in all_tasks if t.status == s) for s in TaskStatus}

    filtered = [t for t in all_tasks if status is None or t.status.value == status]
    filtered = sort_tasks(filtered, sort)

    total_pages = max(1, -(-len(filtered) // TASKS_PER_PAGE))  # ділення з округленням вгору
    page = min(args.get("page", 1), total_pages)

    start = (page - 1) * TASKS_PER_PAGE
    page_tasks = filtered[start:start + TASKS_PER_PAGE]

    return render_template(
        "tasks.html",
        tasks=page_tasks,
        total_all=len(all_tasks),
        total=len(filtered),
        counts=counts,
        statuses=TaskStatus,
        sort_options=SORT_OPTIONS,
        current_status=status,
        current_sort=sort,
        # для url_for: None не потрапляє в адресу
        status_param=status,
        sort_param=args.get("sort"),
        page=page,
        total_pages=total_pages,
    )


@app.route("/tasks/<int:task_id>")
def task_detail(task_id: int):
    task = next((t for t in get_tasks() if t.id == task_id), None)
    if task is None:
        abort(404)

    return render_template("task_detail.html", task=task, list_args=get_list_args())


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
            all_tasks.append(
                Task(new_id, title, TaskStatus(status), created_at=datetime.now().replace(microsecond=0))
            )
            save_tasks(all_tasks)
            # за замовчуванням спочатку нові, тож нова задача буде першою на 1-й сторінці
            return redirect(url_for("tasks"))

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

    list_args = get_list_args()
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
            return redirect(url_for("task_detail", task_id=task.id, **list_args))

    return render_template(
        "task_form.html",
        heading=f"Редагування задачі #{task.id}",
        action_url=url_for("edit_task", task_id=task.id, **list_args),
        cancel_url=url_for("task_detail", task_id=task.id, **list_args),
        statuses=TaskStatus,
        error=error,
        title=title,
        selected_status=status,
    )


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id: int):
    all_tasks = get_tasks()
    task = next((t for t in all_tasks if t.id == task_id), None)
    if task is None:
        abort(404)

    all_tasks.remove(task)
    save_tasks(all_tasks)

    # повертаємось у той самий список (фільтр, сортування, сторінка);
    # якщо сторінка спорожніла, /tasks сам перекине на останню
    return redirect(url_for("tasks", **get_list_args()))


if __name__ == "__main__":
    app.run(debug=True, port=8000)
