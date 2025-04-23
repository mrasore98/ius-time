from datetime import timedelta


from ius_time.db_sqlmodel import Session, Status, Task, select
from ius_time.filters import FilterEnum
from ius_time.utils import datetime_pst


def test_start_task_no_category(database_testing, request):
    tm = database_testing
    new_task_name = request.node.name
    
    # Show task does not exist at start of test
    with Session(tm.db_engine) as session:
        query = select(Task).where(Task.name == new_task_name)
        empty_row = session.exec(query).first()
        assert empty_row is None

    # Confirm task is started
    tm.start_task(new_task_name)
    
    with Session(tm.db_engine) as session:
        query = select(Task).where(Task.name == new_task_name)
        task_list = session.exec(query).all()
        assert len(task_list) == 1
        assert task_list[0].name == new_task_name


def test_start_task_with_category(database_testing, request):
    tm = database_testing
    new_task_name = request.node.name
    category = "test"
    
    # Show task does not exist at start of test
    with Session(tm.db_engine) as session:
        query = select(Task).where(Task.name == new_task_name, Task.category == category)
        empty_row = session.exec(query).first()
        assert empty_row is None

    # Confirm task is started
    tm.start_task(new_task_name, category=category)
    
    with Session(tm.db_engine) as session:
        query = select(Task).where(Task.name == new_task_name, Task.category == category)
        task_list = session.exec(query).all()
        assert len(task_list) == 1
        assert task_list[0].name == new_task_name
        assert task_list[0].category == category


def test_end_task(database_testing):
    tm = database_testing

    # Start tasks to end
    tasks_to_start = ["Task_A", "Task_B", "Task_C"]
    for task in tasks_to_start:
        tm.start_task(task)

    # Query the number of active tasks
    with Session(tm.db_engine) as session:
        active_query = select(Task).where(Task.status == Status.ACTIVE)
        active_task_rows = session.exec(active_query).all()
        num_active_tasks = len(active_task_rows)
        assert len(tasks_to_start) == num_active_tasks

    for idx, task in enumerate(tasks_to_start, 1):
        expected_rows = num_active_tasks - idx
        tm.end_task(task)

        with Session(tm.db_engine) as session:
            active_query = select(Task).where(Task.status == Status.ACTIVE)
            active_task_rows = session.exec(active_query).all()
            rows_after_end_call = len(active_task_rows)
            assert rows_after_end_call == expected_rows


def test_end_last(database_testing):
    pass


def test_end_all_active(database_testing):
    tm = database_testing

    # Start tasks to end
    tasks_to_start = ["Task_A", "Task_B", "Task_C"]
    for task in tasks_to_start:
        tm.start_task(task)

    # Query the number of active tasks
    with Session(tm.db_engine) as session:
        active_query = select(Task).where(Task.status == Status.ACTIVE)
        active_task_rows = session.exec(active_query).all()
        num_active_tasks = len(active_task_rows)
        assert len(tasks_to_start) == num_active_tasks

    tm.end_all_active()

    with Session(tm.db_engine) as session:
        active_query = select(Task).where(Task.status == Status.ACTIVE)
        active_task_rows = session.exec(active_query).all()
        rows_after_end_call = len(active_task_rows)
        assert rows_after_end_call == 0


def test_list_active(database_testing):
    tm = database_testing

    tasks_to_start = ["Task_A", "Task_B", "Task_C", "Task_D", "Task_E"]
    for task in tasks_to_start:
        tm.start_task(task)

    # End 2 tasks to ensure only active are listed
    tm.end_task("Task_B")
    tm.end_task("Task_D")
    expected_active = len(tasks_to_start) - 2

    num_active = len(tm.list_active())

    assert num_active == expected_active


def test_list_complete(database_testing):
    tm = database_testing

    tasks_to_start = ["Task_A", "Task_B", "Task_C", "Task_D", "Task_E"]
    for task in tasks_to_start:
        tm.start_task(task)

    # End 2 tasks to ensure only complete are listed
    tm.end_task("Task_B")
    tm.end_task("Task_D")
    expected_complete = 2

    num_complete = len(tm.list_complete())

    assert num_complete == expected_complete


def test_list_all(database_testing):
    tm = database_testing

    tasks_to_start = ["Task_A", "Task_B", "Task_C", "Task_D", "Task_E"]
    for task in tasks_to_start:
        tm.start_task(task)

    # End 2 tasks to ensure all tasks are listed
    tm.end_task("Task_B")
    tm.end_task("Task_D")
    expected_tasks = len(tasks_to_start)

    num_tasks = len(tm.list_all())

    assert num_tasks == expected_tasks


def test_sum_task_times(database_testing):
    tm = database_testing

    def add_completed_task(task_name: str, duration: int, category: str):
        start_time = datetime_pst.now()
        end_time = start_time + timedelta(seconds=duration)
        total_time = timedelta(seconds=duration)
        
        with Session(tm.db_engine) as session:
            task = Task(
                name=task_name,
                start_time=start_time,
                end_time=end_time,
                total_time=total_time,
                category=category,
                status=Status.COMPLETE
            )
            session.add(task)
            session.commit()

    completed_tasks = [
        ("Task A", 300, "Category A"),
        ("Task B", 65, "Category B"),
        ("Task C", 1800, "Category A"),
        ("Task D", 4500, "Category B"),
        ("Misc Task", 600, "Misc"),
    ]

    # Account for expected task durations
    expected_category_a_total = sum(
        task[1] for task in completed_tasks if task[2] == "Category A"
    )
    expected_category_b_total = sum(
        task[1] for task in completed_tasks if task[2] == "Category B"
    )
    expected_all_category_total = sum(task[1] for task in completed_tasks)

    # Add tasks to database
    for task in completed_tasks:
        add_completed_task(*task)

    summed_times_rows = tm.sum_task_times()

    returned_category_a_total = sum(
        row[1] for row in summed_times_rows if row[0] == "Category A"
    )
    returned_category_b_total = sum(
        row[1] for row in summed_times_rows if row[0] == "Category B"
    )
    returned_all_category_total = sum(row[1] for row in summed_times_rows)

    assert returned_category_a_total == expected_category_a_total
    assert returned_category_b_total == expected_category_b_total
    assert returned_all_category_total == expected_all_category_total


def test_filtered_list(filter_test):
    tm = filter_test

    expected_event_nums = [1, 2, 3, 4, 5, 6, 8]
    for filter_, expected_event_num in zip(FilterEnum, expected_event_nums):
        returned_event_num = len(tm.list_all(filter_))
        assert returned_event_num == expected_event_num


def test_filtered_total(filter_test):
    abs_tolerance_s = 1  # Upper bound for difference

    # Create tasks and make sure they are completed
    tm = filter_test
    tm.end_all_active()

    # Apply Month filter to sum_task_times (default filter)
    summed_rows = tm.sum_task_times()
    total_time = sum(row[1] for row in summed_rows)

    # Sum of tasks "Day", "Week", "Month"
    expected_time = (
        timedelta(seconds=3600 * 22) + timedelta(days=5) + timedelta(days=25)
    ).total_seconds()
    assert abs(expected_time - total_time) < abs_tolerance_s


def test_category_total(filter_test):
    abs_tolerance_s = 1  # Upper bound for difference

    tm = filter_test
    tm.end_all_active()

    # Sum of tasks "Within a Year", "Month" from filter_test (Category B only)
    expected_total = (timedelta(days=300) + timedelta(days=25)).total_seconds()

    returned_rows = tm.sum_task_times(FilterEnum.NONE, "Category B")
    returned_total = sum(row[1] for row in returned_rows)

    assert abs(expected_total - returned_total) < abs_tolerance_s
