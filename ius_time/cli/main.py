""" Command line interface for ius_time. """
import typer

from ius_time import DEFAULT_FILTER, console
from ius_time import task_manager as tm
from ius_time.cli import end_tasks, lists
from ius_time.filters import FilterEnum
from ius_time.table_outputs import total_rows_as_table

app = typer.Typer()
app.add_typer(lists.app, name="list", help="List tasks, with an optional time filter.")
app.add_typer(end_tasks.app, name="end", help="End active tasks.")


@app.command(help="Start a new task.")
def start(task_name: str,
          category: str = typer.Option(
              "Misc",
              "-c",
              "--category")
          ):
    tm.start_task(task_name, category=category)


@app.command(help="Sum the amount of time spent on your tasks. Only calculated for completed tasks")
def total(
        filter_: FilterEnum = DEFAULT_FILTER,
        category: str = typer.Option(None,
                                     "-c",
                                     "--category")
        ):
    rows = tm.sum_task_times(filter_, category=category)
    table_name = "Total Time"
    if category is not None:
        table_name += f" for {category}"
    if filter_ != FilterEnum.NONE:
        table_name += f" ({filter_})"
    table = total_rows_as_table(rows, table_name)
    console.print(table)


def main():
    tm.create_task_table()
    app()


if __name__ == "__main__":
    main()
