import reflex as rx

from ius_time import task_manager
from .models import Task

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


class ActiveTaskHandler(rx.State):
    selected_task: Task = None

    def end_task(self):
        """
        self.selected_task = get row where button was pressed
        task_manager.end_task(self.selected_task.name)
        """
        pass

def active_task_row(task: Task) -> rx.Component:
    return rx.table.row(
        rx.table.cell(task.name),
        rx.table.cell(
            rx.moment(task.start_time, from_now_during=MS_PER_QUARTER, format="YYYY-MM-DD HH:mm:ss")
        ),
        rx.table.cell(task.category),
        rx.table.cell(
            rx.button("End Task", color_scheme="ruby", on_click=ActiveTaskHandler.end_task)
        )
    )

def active_tasks_table(tasks: list[Task]) -> rx.Component:
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
            rx.foreach(tasks, active_task_row)
        )
    )

def completed_tasks_table() -> rx.Component:
    return rx.text("Placeholder for completed tasks table")
