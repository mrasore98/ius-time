# ruff: noqa: F403, F405
from fasthtml.common import *

from ius_time import task_manager
from ius_time.db import DB_PATH, Status
from ius_time.utils import TaskTime, format_timestamp

db = database(DB_PATH)
tasks = db.t.tasks
if tasks not in db.t:
    tasks.create(
        id=int,
        name=str,
        start_time=float,
        end_time=float,
        total_time=float,
        categorty=str,
        status=str,
        pk="id",
        not_null=["id", "name", "start_time", "category", "status"],
    )
Task = tasks.dataclass()

app = FastHTML(hdrs=(picolink, SortableJS()))
rt = app.route


def mk_active_row(task: Task):
    end_task = Button("End Task", hx_post=f"end/{task.id}")
    return Tr(
        Td(task.name),
        Td(format_timestamp(task.start_time)),
        Td(task.category),
        Td(end_task),
        id=f"active-task-{task.id}",
    )


def mk_completed_row(task: Task):
    return Tr(
        Td(task.name),
        Td(format_timestamp(task.start_time)),
        Td(format_timestamp(task.end_time)),
        Td(str(TaskTime(task.total_time))),
        Td(task.category),
        id=f"complete-task-{task.id}",
    )


def active_tasks_table():
    return Table(
        Thead(Tr(Th("Name"), Th("Start Time"), Th("Category"), Th("Action"))),
        Tbody(
            *(
                mk_active_row(Task(**task))
                for task in tasks.rows_where("status = ?", [Status.ACTIVE.value])
            )
        ),
        id="active-tasks-table",
        hx_swap_oob="true",
    )


def completed_tasks_table():
    return Table(
        Thead(
            Tr(
                Th("Name"),
                Th("Start Time"),
                Th("End Time"),
                Th("Total Time"),
                Th("Category"),
            )
        ),
        Tbody(
            *(
                mk_completed_row(Task(**task))
                for task in tasks.rows_where("status = ?", [Status.COMPLETE.value])
            )
        ),
        id="completed-tasks-table",
        hx_swap_oob="true",
    )


@rt("/")
def get():
    new_task_name = Input(id="new-task-name", name="name", placeholder="New Task")
    new_task_category = Input(
        id="new-category-name", name="category", placeholder="Category"
    )
    add = Form(
        Group(new_task_name, new_task_category, Button("Start")),
        hx_post="/",
        target_id="active-tasks-table",
        hx_swap="afterbegin",
    )
    active_tasks = Div(H1("Active Tasks"), active_tasks_table())
    completed_tasks = Div(H1("Completed Tasks"), completed_tasks_table())
    return Titled("IUS Time", H2("Start New Task"), add, active_tasks, completed_tasks)


@rt("/")
def post(task: Task):
    new_name_inp = Input(
        id="new-task-name", name="name", placeholder="Task Name", hx_swap_oob="true"
    )
    new_category_inp = Input(
        id="new-category-name",
        name="category",
        placeholder="Category",
        hx_swap_oob="true",
    )
    if not task.category:
        task.category = "Misc"
    task_manager.start_task(task.name, task.category)
    return new_name_inp, new_category_inp


@rt("/end/{id}")
def post(id: int):
    task_to_end = [Task(**task) for task in tasks.rows_where("id = ?", [id])][0]
    task_manager.end_task(task_to_end.name)


if __name__ == "__main__":
    serve(host="127.0.0.1")
