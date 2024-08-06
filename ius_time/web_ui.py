# ruff: noqa: F403, F405
from fasthtml.common import *

from ius_time.db import DB_PATH, Status

db = database(DB_PATH)
tasks = db.t.tasks
if tasks not in db.t:
    tasks.create(id=int,
                 name=str,
                 start_time=float,
                 end_time=float,
                 total_time=float,
                 categorty=str,
                 status=str,
                 pk="id",
                 not_null=["id", "name", "start_time", "category", "status"])
Task = tasks.dataclass()

app = FastHTMLWithLiveReload(hdrs=(picolink, SortableJS()))
rt = app.route


def mk_active_row(task: Task):
    return Tr(Td(task.name), Td(task.start_time), Td(task.category), Td(Button("End Task")), id=f"active-task-{task.id}")


def mk_completed_row(task: Task):
    return Tr(Td(task.name), Td(task.start_time), Td(task.end_time), Td(task.total_time), Td(task.category), id=f"complete-task-{task.id}")


def active_tasks_table():
    return Table(
        Thead(Tr(Th("Name"), Th("Start Time"), Th("Category"), Th("Action"))),
        Tbody(
            *(mk_active_row(Task(**task)) for task in
              db.q(f'select * from {tasks} where {tasks.c.status} = "{Status.ACTIVE.value}"'))
        )
    )


def completed_tasks_table():
    return Table(
        Thead(Tr(Th("Name"), Th("Start Time"), Th("End Time"), Th("Total Time"), Th("Category"))),
        Tbody(
            *(mk_completed_row(Task(**task)) for task in
              db.q(f'select * from {tasks} where {tasks.c.status} = "{Status.COMPLETE.value}"'))
        )
    )


@rt("/")
def get():
    return Titled(
        "IUS Time",

        Div(
            H1("Active Tasks"),
            active_tasks_table()
        ),
        Div(
            H1("Completed Tasks"),
            completed_tasks_table()
        )

    )


if __name__ == "__main__":
    serve(host="127.0.0.1")
