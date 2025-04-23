import typer

from ius_time import DEFAULT_FILTER, console
from ius_time import task_manager as tm
from ius_time.filters import FilterEnum
from ius_time.table_outputs import list_rows_as_table

app = typer.Typer()


@app.command(help="List all tasks in the database.")
def all(filter_: FilterEnum = DEFAULT_FILTER):
    rows = tm.list_all(filter_)
    if len(rows) == 0:
        console.print("[error]No tasks to list[/error]")
        return
    table_name = "All Tasks"
    if filter_ != FilterEnum.NONE:
        table_name += f" ({filter_!s})"
    table = list_rows_as_table(rows, table_name)
    console.print(table)


@app.command(help="List only active tasks.")
def active(filter_: FilterEnum = DEFAULT_FILTER):
    rows = tm.list_active(filter_)
    if len(rows) == 0:
        console.print("[error]No active tasks to list[/error]")
        return
    table_name = "Active Tasks"
    if filter_ != FilterEnum.NONE:
        table_name += f" ({filter_!s})"
    table = list_rows_as_table(rows, table_name)
    console.print(table)


@app.command(help="List only completed tasks.")
def complete(filter_: FilterEnum = DEFAULT_FILTER):
    rows = tm.list_complete(filter_)
    if len(rows) == 0:
        console.print("[error]No completed tasks[/error]")
        return
    table_name = "Completed Tasks"
    if filter_ != FilterEnum.NONE:
        table_name += f" ({filter_!s})"
    table = list_rows_as_table(rows, table_name)
    console.print(table)


if __name__ == "__main__":
    app()
