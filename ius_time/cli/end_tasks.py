import sqlite3

import typer

from ius_time import console
from ius_time import task_manager as tm

app = typer.Typer()


@app.command(help="Specify the name of the task to end.")
def task(task_name: str):
    try:
        if not tm.end_task(task_name):
            raise typer.Exit(1)
    except sqlite3.Error:
        raise typer.Exit(3)


@app.command(help="End the last task that was started.")
def last():
    try:
        if not tm.end_last():
            raise typer.Exit(1)
    except sqlite3.Error:
        raise typer.Exit(3)


@app.command(help="End all active tasks.")
def all():
    end_all = typer.confirm("Are you sure you want to end all active tasks?")
    if end_all:
        try:
            if not tm.end_all_active():
                raise typer.Exit(1)
        except sqlite3.Error:
            raise typer.Exit(3)
    else:
        console.print("Operation [blue italic]\"end all\"[/] aborted!")


if __name__ == "__main__":
    app()
