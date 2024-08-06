""" Miscellaneous utilities to support ius_time. """
from sqlite3 import Row
from zoneinfo import ZoneInfo

from heliclockter import datetime_tz
from rich.table import Table
from rich.theme import Theme

ius_theme = Theme({
    "info": "blue underline",
    "success": "italic green",
    "error": "bold red",
    "title": "bold underline",
    "task": "blue italic",
})

datetime_format = "%a %m/%d/%Y %I:%M:%S %p"


class datetime_pst(datetime_tz):
    """ A 'datetime_tz' that matches the timezone for San Francisco. """
    assumed_timezone_for_timezone_naive_input = ZoneInfo("America/Los_Angeles")


def format_timestamp(timestamp: float):
    return datetime_pst.fromtimestamp(timestamp, tz=ZoneInfo("America/Los_Angeles")).strftime(datetime_format)


class TaskTime:
    """ Custom class for handling reporting of task times."""

    def __init__(self, total_seconds: int):
        self.raw = total_seconds
        self.hours = int(total_seconds // 3600)
        remainder = total_seconds % 3600
        self.minutes = int(remainder // 60)
        remainder %= 60
        self.seconds = int(remainder)

    def __str__(self):
        return f"{self.hours}h {self.minutes}m {self.seconds}s"


def list_rows_as_table(rows: list[Row], table_name: str = "Table") -> Table:
    table = Table(title=table_name, title_style="title", highlight=True)
    # Pull column names from Row keys
    for idx, row in enumerate(rows):
        if idx == 0:
            for key in row.keys():
                split_key = key.split("_")
                sep_key = " ".join(split_key).capitalize()
                table.add_column(sep_key)

    # Format columns with numerical values
    writable_rows = [[row[i] for i in range(len(row))] for row in rows]
    for row in writable_rows:
        for idx in range(2, 5):
            if isinstance(row[idx], float):  # Do not need to recast None type
                if idx in [2, 3]:  # Start and end times
                    row[idx] = datetime_pst.fromtimestamp(row[idx], tz=ZoneInfo("America/Los_Angeles")).strftime(datetime_format)
                elif idx == 4:  # Total time
                    row[idx] = TaskTime(row[idx])
        table.add_row(*[str(row[i]) for i in range(len(row))])
    return table


def total_rows_as_table(rows: list[Row], table_name: str = "Task Totals"):
    table = Table(title=table_name, title_style="title", highlight=True)
    table.add_column("Category")
    table.add_column("Total Time")
    table.add_column("Percentage")

    categories = []
    task_times = []
    total_time_s = 0
    for row in rows:
        categories.append(row[0])
        task_times.append(row[1])
        total_time_s += row[1]

    for category, time in zip(categories, task_times):
        task_time = TaskTime(time)
        table.add_row(category, str(task_time), f"{time/total_time_s * 100:.2f}")

    return table
