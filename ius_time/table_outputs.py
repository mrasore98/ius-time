from rich.table import Table

from ius_time.db import Status, Task
from ius_time.utils import TaskTime, datetime_format


# TODO add nicer formatting to list table using TaskTime to format raw times
def list_rows_as_table(rows: list[Task], table_name: str = "Table") -> Table:
    table = Table(title=table_name, title_style="title", highlight=True)
    col_names = ["Id", "Name", "Start time", "End time", "Total time", "Category", "Status"]
    for col_name in col_names:
        table.add_column(col_name)
    
    for row in rows:
        fmt_end_time, fmt_total_time = None, None
        fmt_start_time = row.start_time.strftime(datetime_format)
        if row.status == Status.COMPLETE:
            # end_time and total_time should have populated values if task is complete
            fmt_end_time = row.end_time.strftime(datetime_format)
            fmt_total_time = TaskTime(row.total_time.total_seconds())
        table.add_row(*map(str, (row.id, row.name, fmt_start_time, fmt_end_time, fmt_total_time, row.category, row.status)))
    return table


def total_rows_as_table(rows: list[tuple[str, int]], table_name: str = "Task Totals"):
    table = Table(title=table_name, title_style="title", highlight=True)
    table.add_column("Category")
    table.add_column("Total Time")
    table.add_column("Percentage")

    total_time_s = sum(time for _, time in rows)
    for category, time in rows:
        task_time = TaskTime(time)
        table.add_row(category, str(task_time), f"{time/total_time_s * 100:.2f}")
    return table
