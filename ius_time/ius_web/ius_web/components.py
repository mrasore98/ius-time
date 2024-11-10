import reflex as rx
from reflex.components.radix.themes.components.segmented_control import on_value_change

from .models import Task

class NewTaskState(rx.State):
    """State for new task input."""
    name: str = ""
    category: str = ""

    def start_task(self):
        # TODO create new task in database
        self.name = ""
        self.category = ""

def task_input() -> rx.Component:
    return rx.hstack(
        rx.input(value=NewTaskState.name, placeholder="New Task", on_change=NewTaskState.set_name, required=True),
        rx.input(value=NewTaskState.category, placeholder="Category", on_change=NewTaskState.set_category),
        rx.button("Start", on_click=NewTaskState.start_task)
    )

def active_tasks_table() -> rx.Component:
    return rx.text("Placeholder for active tasks table")

def completed_tasks_table() -> rx.Component:
    return rx.text("Placeholder for completed tasks table")
