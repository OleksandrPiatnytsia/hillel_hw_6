from flask import Flask, render_template

from models.clases import Task
from serialization.json_serialization import JsonDataSerialization

app = Flask(__name__)


def get_tasks() -> list[Task]:
    return [Task.from_dict(item) for item in JsonDataSerialization.load_tasks()]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tasks")
def tasks():
    return render_template("tasks.html", tasks=get_tasks())


if __name__ == "__main__":
    app.run(debug=True, port=8000)
