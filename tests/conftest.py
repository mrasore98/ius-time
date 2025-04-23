from pathlib import Path

import pytest
from sqlalchemy import text

from ius_time.db import Session, Status, Task
from ius_time.db import TaskManager as SqlModelTaskManager
from ius_time.utils import datetime_pst

TEST_DB = Path(".", "test_db.db")


def setup_test_db(manager: SqlModelTaskManager):
    manager.create_task_table()


def reset_test_db(manager: SqlModelTaskManager):
    with Session(manager.db_engine) as session:
        session.exec(text("DROP TABLE task"))
        session.commit()


@pytest.fixture(scope="module")
def _create_remove_db():
    """Teardown-only fixture to remove the test database."""
    yield
    TEST_DB.unlink()


@pytest.fixture
def database_testing(_create_remove_db):
    """
    Creates/connects the test database and yields a test-specific TaskManager.

    On setup, create the `task` table and customize the connection to easily call `:execute:` for SQL queries.
    On teardown, the `task` table is dropped and the connection is closed.
    """
    tm = SqlModelTaskManager(TEST_DB)
    setup_test_db(tm)
    yield tm
    reset_test_db(tm)


def add_active_task(
    manager: SqlModelTaskManager,
    task_name: str,
    start_time: datetime_pst,
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
    # sql = "INSERT INTO tasks \
    # (name, start_time, category, status) VALUES \
    # (?, ?, ?, ?)"
    # with manager.connection:
    #     manager.connection.execute(sql, [task_name, start_time, category, manager.status.ACTIVE])
    with Session(manager.db_engine) as session:
        session.add(
            Task(
                name=task_name,
                start_time=start_time,
                category=category,
                status=Status.ACTIVE,
            )
        )
        session.commit()


@pytest.fixture
def filter_test(database_testing):
    """Create active tasks with start times corresponding to each filter."""
    tm = database_testing

    active_tasks = [
        ("First Task", datetime_pst.past(days=1000), "Misc"),
        ("Over a Year", datetime_pst.past(days=400), "Category A"),
        ("Within a Year", datetime_pst.past(days=300), "Category B"),
        ("Semiannual", datetime_pst.past(weeks=23), "Misc"),
        ("Quarter", datetime_pst.past(weeks=10), "Category A"),
        ("Month", datetime_pst.past(days=25), "Category B"),
        ("Week", datetime_pst.past(days=5), "Misc"),
        ("Day", datetime_pst.past(seconds=3600 * 22), "Category A"),
    ]

    for task in active_tasks:
        add_active_task(tm, *task)

    yield tm


@pytest.fixture
def cli_testing(_create_remove_db):
    # Set up SQLModel TaskManager for CLI testing
    tm = SqlModelTaskManager(TEST_DB)
    setup_test_db(tm)
    yield tm
    reset_test_db(tm)
