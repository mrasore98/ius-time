""" Miscellaneous utilities to support ius_time. """
from zoneinfo import ZoneInfo

from heliclockter import datetime_tz
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


class TaskTime:
    """ Custom class for handling reporting of task times."""

    def __init__(self, total_seconds: int | float):
        self.raw = total_seconds
        self.hours = int(total_seconds // 3600)
        remainder = total_seconds % 3600
        self.minutes = int(remainder // 60)
        remainder %= 60
        self.seconds = int(remainder)

    def __str__(self):
        return f"{self.hours}h {self.minutes}m {self.seconds}s"
