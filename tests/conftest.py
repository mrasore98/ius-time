import sqlite3
from pathlib import Path

import pytest

from ius_time import task_manager
from ius_time.db import TaskManager
from ius_time.utils import datetime_pst

TEST_DB = Path(".", "test_db.db")


def setup_test_db(manager: TaskManager):
    # Expose method for ease of testing
    manager.execute = manager.connection.execute
    manager.create_task_table()


def reset_test_db(manager: TaskManager):
    manager.connection.execute("DROP TABLE tasks")
    manager.close()


@pytest.fixture(scope="module")
def _create_remove_db():
    """ Teardown-only fixture to remove the test database. """
    yield
    TEST_DB.unlink()


@pytest.fixture
def database_testing(_create_remove_db):
    """
    Creates/connects the test database and yields a test-specific TaskManager.

    On setup, create the `task` table and customize the connection to easily call `:execute:` for SQL queries.
    On teardown, the `task` table is dropped and the connection is closed.
    """
    tm = TaskManager(TEST_DB)
    setup_test_db(tm)
    yield tm
    reset_test_db(tm)


def add_active_task(
        manager: TaskManager,
        task_name: str,
        start_time: float,
        category: str = "Misc",
):
    """
    Helper function to add active tasks to the database associated with the given TaskManager.

    :param manager: TaskManager with an open connection to the database where tasks will be added.
        Assumes the default table `tasks` has been created.
    :param task_name: Name of the task to add.
    :param start_time: Start time of the task as a timestamp.
    :param category: Optional category of the task to add.
    :return:
    """
    sql = "INSERT INTO tasks \
    (name, start_time, category, status) VALUES \
    (?, ?, ?, ?)"
    with manager.connection:
        manager.connection.execute(sql, [task_name, start_time, category, manager.status.ACTIVE])


@pytest.fixture
def filter_test(database_testing):
    """ Create active tasks with start times corresponding to each filter. """
    tm = database_testing

    active_tasks = [
        ("First Task", 10, "Misc"),
        ("Over a Year", datetime_pst.past(days=400).timestamp(), "Category A"),
        ("Within a Year", datetime_pst.past(days=300).timestamp(), "Category B"),
        ("Semiannual", datetime_pst.past(weeks=23).timestamp(), "Misc"),
        ("Quarter", datetime_pst.past(weeks=10).timestamp(), "Category A"),
        ("Month", datetime_pst.past(days=25).timestamp(), "Category B"),
        ("Week", datetime_pst.past(days=5).timestamp(), "Misc"),
        ("Day", datetime_pst.past(seconds=3600*22).timestamp(), "Category A"),
    ]

    for task in active_tasks:
        add_active_task(tm, *task)

    yield tm


@pytest.fixture
def cli_testing(_create_remove_db):
    # Have to use the same TaskManager object as the app
    tm = task_manager
    tm.close()
    # Change the database location for testing
    tm._connection = sqlite3.connect(TEST_DB)
    tm.connection.row_factory = sqlite3.Row
    setup_test_db(tm)
    yield tm
    reset_test_db(tm)
