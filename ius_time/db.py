""" Database objects and operations related to task management. """
import sqlite3
from enum import StrEnum
from pathlib import Path

from rich.console import Console

from ius_time.filters import FilterEnum, parse_filter
from ius_time.utils import TaskTime, datetime_format, datetime_pst, ius_theme

# TODO: Make database location configurable
DB_PATH = Path(__file__).parent.parent.resolve() / "ius-tasks.db"


class Status(StrEnum):
    ACTIVE = "Active"
    COMPLETE = "Complete"


class TaskManager:
    """ Primary class for managing tasks in the database. """

    status = Status

    def __init__(self, db_path: Path = DB_PATH):
        self._connection = sqlite3.connect(db_path)
        self._connection.row_factory = sqlite3.Row
        self.console = Console(theme=ius_theme)

    @property
    def connection(self) -> sqlite3.Connection:
        return self._connection

    def close(self):
        self._connection.close()

    def create_task_table(self) -> bool:
        """
        Creates a default table named 'tasks' if one does not yet exist.

        :return: Boolean confirming existence of table.
        """
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS tasks (\
                    id INTEGER PRIMARY KEY NOT NULL, \
                    name TEXT NOT NULL, \
                    start_time INTEGER NOT NULL, \
                    end_time INTEGER, \
                    total_time INTEGER, \
                    category TEXT NOT NULL, \
                    status TEXT NOT NULL\
                    )"
        )

        confirmation = self._connection.execute("SELECT name FROM sqlite_master WHERE name='tasks'")
        return confirmation.fetchone() is not None

    # START FUNCTIONS
    def start_task(self, task_name: str, category: str = "Misc"):
        # TODO: Add data validation for task name to ensure unique (only compare to active tasks)
        start_task_time_dt = datetime_pst.now()
        self.console.print(f"Starting task [info]{task_name}[/] at [info]{start_task_time_dt.strftime(datetime_format)}[/]")
        start_time = start_task_time_dt.timestamp()
        try:
            with self._connection:
                self._connection.execute(
                    "INSERT INTO tasks (name, start_time, category, status) VALUES(?, ?, ?, ?)",
                    [task_name, start_time, category, self.status.ACTIVE])
        except sqlite3.Error:
            self.console.print(f"[error]Could not start task [info]{task_name}[/info]![/error]")

    # END FUNCTIONS
    def end_task(self, task_name: str) -> bool:
        end_time_dt = datetime_pst.now()

        self.console.print(f"Ending task [info]{task_name}[/] at [info]{end_time_dt.strftime(datetime_format)}[/]")

        start_time_result_row = self._connection.execute("SELECT start_time FROM tasks WHERE name = ? AND status = "
                                                         "?",
                                                         [task_name, self.status.ACTIVE]).fetchone()
        if start_time_result_row is not None:
            start_time = start_time_result_row["start_time"]
        else:
            self.console.print(f"[error][info]{task_name}[/info] is not an Active Task!")
            return False

        end_time = end_time_dt.timestamp()
        total_time = end_time - start_time

        try:
            with self._connection:
                self._connection.execute(
                    "UPDATE tasks SET end_time = ?, total_time = ?, status = ? WHERE name = ?",
                    [end_time, total_time, self.status.COMPLETE, task_name]
                )

            # TODO: Randomize success emoji
            self.console.print(f"[success]Task [info]{task_name}[/info] ended after [info]{TaskTime(total_time)!s}[/info] :100:")
            return True
        except sqlite3.Error:
            self.console.print(f"[error]Could not end task [info]{task_name}[/info]![/error]")
            raise

    def end_last(self) -> bool:
        last_task_result = (self._connection.execute(
            "SELECT name FROM tasks WHERE start_time = (SELECT MAX(start_time) FROM tasks WHERE status = ?)",
            [self.status.ACTIVE])
                            .fetchone())
        if last_task_result is not None:
            return self.end_task(last_task_result["name"])
        else:
            self.console.print("[error]No active tasks to end!")
            return False

    def end_all_active(self) -> bool:
        end_time_dt = datetime_pst.now()
        end_time = end_time_dt.timestamp()

        # Get the number of active tasks
        resp = self._connection.execute("SELECT * FROM tasks WHERE status = ?", [self.status.ACTIVE])
        num_tasks = len(resp.fetchall())

        if num_tasks > 0:
            try:
                with self._connection:
                    # Update the end time first for use in calculating total time
                    self._connection.execute("UPDATE tasks SET end_time = ? WHERE status = ?",
                                             [end_time, self.status.ACTIVE])
                    # Update the total time and set status to complete
                    self._connection.execute(
                        "UPDATE tasks SET total_time = (end_time - start_time), status = ? WHERE status = ?",
                        [self.status.COMPLETE, self.status.ACTIVE]
                    )

                self.console.print(
                    f"[success]Ended [info]{num_tasks}[/info] tasks at [info]{end_time_dt.strftime(datetime_format)}[/info]")
                return True
            except sqlite3.Error:
                self.console.print("[error]An error occurred during attempt to end all active tasks!")
                raise
        else:
            self.console.print("[error]No active tasks to end!")
            return False

    # LIST FUNCTIONS
    def list_active(self, filter_: FilterEnum = FilterEnum.MONTH) -> list[sqlite3.Row]:
        start_time = parse_filter(filter_)
        resp = self._connection.execute(
            "SELECT * FROM tasks WHERE status = ? AND start_time > ?",
            [self.status.ACTIVE, start_time]
        )
        return resp.fetchall()

    def list_complete(self, filter_: FilterEnum = FilterEnum.MONTH) -> list[sqlite3.Row]:
        start_time = parse_filter(filter_)
        resp = self._connection.execute(
            "SELECT * FROM tasks WHERE status = ? AND start_time > ?",
            [self.status.COMPLETE, start_time]
        )
        return resp.fetchall()

    def list_all(self, filter_: FilterEnum = FilterEnum.MONTH) -> list[sqlite3.Row]:
        start_time = parse_filter(filter_)
        resp = self._connection.execute(
            "SELECT * FROM tasks WHERE start_time > ?",
            [start_time]
        )
        return resp.fetchall()

    # TOTAL FUNCTIONS
    def sum_task_times(self, filter_: FilterEnum = FilterEnum.MONTH, category: str = None) -> list[sqlite3.Row]:
        start_time = parse_filter(filter_)

        if category is None:
            resp = self._connection.execute("SELECT category, SUM(total_time) FROM tasks WHERE start_time > ? \
                GROUP BY category ORDER BY SUM(total_time) DESC", [start_time])
        else:
            resp = self._connection.execute("SELECT category, SUM(total_time) FROM tasks WHERE start_time > ? AND category = ? \
                GROUP BY category ORDER BY SUM(total_time) DESC", [start_time, category])
        return resp.fetchall()
