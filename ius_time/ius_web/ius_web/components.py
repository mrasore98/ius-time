import reflex as rx

from ius_time import task_manager
from ius_time.utils import TaskTime
from .models import Tasks

MS_PER_QUARTER = (1000 * 60 * 60 * 24 * 30 * 3)

class NewTaskState(rx.State):
    """State for new task input."""
    name: str = ""
    category: str = ""

    def start_task(self):
        # Respect default category name if one is not supplied
        args = (self.name, self.category) if self.category else (self.name,)
        task_manager.start_task(*args)
        # Reset input values
        self.name = ""
        self.category = ""

def task_input() -> rx.Component:
    return rx.hstack(
        rx.input(value=NewTaskState.name, placeholder="New Task", on_change=NewTaskState.set_name, required=True),
        rx.input(value=NewTaskState.category, placeholder="Category", on_change=NewTaskState.set_category),
        rx.button("Start", on_click=NewTaskState.start_task)
    )


# class ActiveTaskHandler(rx.ComponentState):
    task: Tasks

    def end_task(self):
        task_manager.end_task(self.task.name)

    @classmethod
    def get_component(cls, **props):
        return rx.table.row(
            rx.table.cell(cls.task.name),
            rx.table.cell(
                formatted_time(cls.task.start_time),
            ),
            rx.table.cell(cls.task.category),
            rx.table.cell(
                rx.button("End Task", color_scheme="ruby", on_click=cls.end_task)
            )
        )

    @classmethod
    def new(cls, task: Tasks):
        instance = cls.create()
        instance.task = task

class ActiveTaskHandler(rx.State):
    selected_task: Tasks = None

    def end_task(self):
        pass


def formatted_time(timestamp: int) -> rx.Component:
    return rx.moment(timestamp, from_now_during=MS_PER_QUARTER, format="YYYY-MM-DDD HH:mm:ss")



def active_task_row(task: Tasks) -> rx.Component:
    return rx.table.row(
        rx.table.cell(task.name, id=task.name),
        rx.table.cell(
            formatted_time(task.start_time),
        ),
        rx.table.cell(task.category),
        rx.table.cell(
            rx.button("End Task", color_scheme="ruby", on_click=ActiveTaskHandler.end_task)
        )
    )

def active_tasks_table(active_tasks: list[Tasks]) -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Name"),
                rx.table.column_header_cell("Start Time"),
                rx.table.column_header_cell("Category"),
                rx.table.column_header_cell("Action"),
            )
        ),
        rx.table.body(
            rx.foreach(active_tasks, active_task_row)
        )
    )

def completed_task_row(task: Tasks) -> rx.Component:
    return rx.table.row(
        rx.table.cell(task.name),
        rx.table.cell(
            formatted_time(task.start_time),
        ),
        rx.table.cell(
            formatted_time(task.end_time),
        ),
        rx.table.cell(task.total_time),  # TODO: format this to use the time appropriately
        rx.table.cell(task.category)
    )

def completed_tasks_table(completed_tasks: list[Tasks]) -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Name"),
                rx.table.column_header_cell("Start Time"),
                rx.table.column_header_cell("End Time"),
                rx.table.column_header_cell("Total Time"),
                rx.table.column_header_cell("Category"),
            )
        ),
        rx.table.body(
            rx.foreach(completed_tasks, completed_task_row)
        )
    )
