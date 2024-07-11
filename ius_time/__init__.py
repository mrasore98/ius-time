import typer
from rich.console import Console

from ius_time.db import TaskManager
from ius_time.filters import FilterEnum
from ius_time.utils import ius_theme

DEFAULT_FILTER = typer.Option(
    FilterEnum.MONTH,
    "--filter",
    "-f",
    help="When applied, limits list output to tasks started within the filter window."
)

task_manager = TaskManager()
console = Console(theme=ius_theme)
