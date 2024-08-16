from typer.testing import CliRunner

from ius_time import TaskManager
from ius_time.cli.main import app
from ius_time.utils import datetime_format, datetime_pst

from .conftest import add_active_task

runner = CliRunner()


def add_generic_tasks(
    manager: TaskManager,
    task_base_name: str,
    num_tasks: int = 5,
    category: str = "Misc",
) -> None:
    for i in range(1, num_tasks + 1):
        add_active_task(
            manager,
            f"{task_base_name}_{i}",
            datetime_pst.past(weeks=i).timestamp(),
            category=category,
        )


class TestStart:
    def test_start(self, cli_testing, request):
        now = datetime_pst.now()
        task_name = request.node.name
        result = runner.invoke(app, ["start", task_name])
        assert result.exit_code == 0
        assert task_name in result.output
        assert str(now.strftime(datetime_format)) in result.output


class TestEnd:
    def test_end_task_active(self, cli_testing, request):
        tm = cli_testing
        task_name = request.node.name
        now = datetime_pst.now()
        add_active_task(tm, task_name, now.timestamp())
        result = runner.invoke(app, ["end", "task", task_name])
        assert result.exit_code == 0
        assert str(now.strftime(datetime_format)) in result.output
        assert f"{task_name} ended after" in result.output

    def test_end_task_not_active(self, cli_testing):
        task_name = "not_active"
        result = runner.invoke(app, ["end", "task", task_name])
        assert result.exit_code == 1
        assert f"{task_name} is not an Active Task" in result.output

    def test_end_last_active(self, cli_testing, request):
        tm = cli_testing
        task_name = request.node.name
        now = datetime_pst.now()
        add_active_task(tm, task_name, now.timestamp())
        result = runner.invoke(app, ["end", "last"])
        assert result.exit_code == 0
        assert str(now.strftime(datetime_format)) in result.output
        assert f"{task_name} ended after" in result.output

    def test_end_last_not_active(self, cli_testing):
        result = runner.invoke(app, ["end", "last"])
        assert result.exit_code == 1
        assert "No active tasks to end!" in result.output

    def test_end_all_confirmed(self, cli_testing, request):
        tm = cli_testing
        num_tasks_to_end = 5
        task_name_base = request.node.name
        add_generic_tasks(tm, task_name_base)
        result = runner.invoke(app, ["end", "all"], input="y")
        assert result.exit_code == 0
        assert f"Ended {num_tasks_to_end}" in result.output

    def test_end_all_not_confirmed(self, cli_testing):
        result = runner.invoke(app, ["end", "all"], input="N")
        assert result.exit_code == 0
        assert 'Operation "end all" aborted' in result.output


class TestList:
    # list_lines_per_task = 3
    #
    # @classmethod
    # def parse_list_tasks(cls, table_output: str) -> (int, list[str]):
    #     # TODO debug this method!
    #     split_table_output = table_output.splitlines()
    #     # Skip headers and end of table
    #     task_lines = split_table_output[4:-1]
    #     return int(len(task_lines) / cls.list_lines_per_task), task_lines

    def test_list_active_no_filter(self, cli_testing, request):
        tm = cli_testing
        task_base_name = request.node.name
        num_expected_tasks = 3
        add_generic_tasks(tm, task_base_name, num_expected_tasks)
        result = runner.invoke(app, ["list", "active"])
        # num_tasks, _ = self.parse_list_tasks(result.output)
        assert result.exit_code == 0
        assert "Active Tasks (month)" in result.output
        # assert num_tasks == num_expected_tasks

    def test_list_complete_no_filter(self, cli_testing, request):
        tm = cli_testing
        task_base_name = request.node.name
        num_expected_tasks = 3
        add_generic_tasks(tm, task_base_name, num_expected_tasks)
        tm.end_all_active()
        result = runner.invoke(app, ["list", "complete"])
        # num_tasks, _ = self.parse_list_tasks(result.output)
        assert result.exit_code == 0
        assert "Completed Tasks (month)" in result.output
        # assert num_tasks == num_expected_tasks

    def test_list_all_no_filter(self, cli_testing, request):
        tm = cli_testing
        task_base_name = request.node.name
        add_generic_tasks(tm, task_base_name)
        tm.end_last()
        tm.end_last()
        result = runner.invoke(app, ["list", "all"])
        assert result.exit_code == 0
        assert "All Tasks (month)" in result.output

    def test_list_active_with_filter(self, cli_testing, request):
        tm = cli_testing
        task_base_name = request.node.name
        num_expected_tasks = 3
        add_generic_tasks(tm, task_base_name, num_expected_tasks)
        result = runner.invoke(app, ["list", "active", "-f", "quarter"])
        # num_tasks, _ = self.parse_list_tasks(result.output)
        assert result.exit_code == 0
        assert "Active Tasks (quarter)" in result.output
        # assert num_tasks == num_expected_tasks

    def test_list_complete_with_filter(self, cli_testing, request):
        tm = cli_testing
        task_base_name = request.node.name
        num_expected_tasks = 3
        add_generic_tasks(tm, task_base_name, num_expected_tasks)
        tm.end_all_active()
        result = runner.invoke(app, ["list", "complete", "-f", "quarter"])
        # num_tasks, _ = self.parse_list_tasks(result.output)
        assert result.exit_code == 0
        assert "Completed Tasks (quarter)" in result.output
        # assert num_tasks == num_expected_tasks

    def test_list_all_with_filter(self, cli_testing, request):
        tm = cli_testing
        task_base_name = request.node.name
        add_generic_tasks(tm, task_base_name)
        tm.end_last()
        tm.end_last()
        result = runner.invoke(app, ["list", "all", "-f", "quarter"])
        assert result.exit_code == 0
        assert "All Tasks (quarter)" in result.output

    def test_list_active_no_tasks(self, cli_testing, request):
        tm = cli_testing
        task_base_name = request.node.name
        num_expected_tasks = 3
        add_generic_tasks(tm, task_base_name, num_expected_tasks)
        tm.end_all_active()
        result = runner.invoke(app, ["list", "active"])
        assert result.exit_code == 0
        assert "No active tasks to list" in result.output

    def test_list_complete_no_tasks(self, cli_testing, request):
        tm = cli_testing
        task_base_name = request.node.name
        num_expected_tasks = 3
        add_generic_tasks(tm, task_base_name, num_expected_tasks)
        result = runner.invoke(app, ["list", "complete"])
        assert result.exit_code == 0
        assert "No completed tasks" in result.output

    def test_list_all_no_tasks(self, cli_testing):
        result = runner.invoke(app, ["list", "all"])
        assert result.exit_code == 0
        assert "No tasks to list" in result.output


class TestTotal:
    def test_total_no_filter(self, cli_testing, request):
        tm = cli_testing
        task_base_name = request.node.name
        add_generic_tasks(tm, task_base_name)
        tm.end_all_active()
        result = runner.invoke(app, ["total"])
        assert result.exit_code == 0
        assert "Total Time (month)" in result.output

    def test_total_with_filter(self, cli_testing, request):
        tm = cli_testing
        task_base_name = request.node.name
        add_generic_tasks(tm, task_base_name)
        tm.end_all_active()
        result = runner.invoke(app, ["total", "-f", "week"])
        assert result.exit_code == 0
        assert "Total Time (week)" in result.output

    def test_total_with_category(self, cli_testing, request):
        tm = cli_testing
        task_base_name = request.node.name
        category = "TotalsUnitTest"
        add_generic_tasks(tm, task_base_name, category=category)
        tm.end_all_active()
        result = runner.invoke(app, ["total", "-c", category])
        assert result.exit_code == 0
        assert f"Total Time for {category} (month)" in result.output
