"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config

from ius_time.db import Status
from .models import Task
from .components import task_input, active_tasks_table, completed_tasks_table


class AppState(rx.State):
    """The app state."""

    tasks: list[Task] = [Task(name="example", start_time=1234, end_time=None, total_time=None, category="Test", status=Status.ACTIVE)]



def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("IUS Time", size="9"),
            task_input(),
            rx.heading("Active Tasks", size="6"),
            active_tasks_table(AppState.tasks),
            rx.heading("Completed Tasks", size="6"),
            completed_tasks_table(),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )


app = rx.App()
app.add_page(index)
