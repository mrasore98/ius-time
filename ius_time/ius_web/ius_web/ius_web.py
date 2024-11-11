"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from sqlmodel import select

from rxconfig import config

from ius_time import task_manager as tm
from ius_time.db import Status
from .models import Tasks
from .components import task_input, active_tasks_table, completed_tasks_table


class AppState(rx.State):
    """The app state."""

    tasks: list[Tasks] = [Tasks(name="example", start_time=999999999, end_time=(999999999 + 30000), total_time=30, category="Test", status=Status.ACTIVE)]
    active_tasks: list[Tasks] = []
    completed_tasks: list[Tasks] = []
    active_task_dict = dict()

    def end_task(self):
        pass

    def update_task_lists(self):
        active_rows = tm.list_active()
        complete_rows = tm.list_complete()
        self.active_tasks = [Tasks(**row) for row in active_rows]
        self.completed_tasks = [Tasks(**row) for row in complete_rows]
        self.active_task_dict = {task: task.name for task in self.active_tasks}


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("IUS Time", size="9"),
            task_input(),
            rx.heading("Active Tasks", size="6"),
            active_tasks_table(AppState.active_tasks),
            rx.heading("Completed Tasks", size="6"),
            completed_tasks_table(AppState.completed_tasks),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )


app = rx.App()
app.add_page(index, on_load=AppState.update_task_lists)
