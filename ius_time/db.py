import itertools as it
from datetime import timedelta
from enum import StrEnum
from pathlib import Path

from rich.console import Console
from sqlmodel import Field, Session, SQLModel, create_engine, func, select

from ius_time.filters import FilterEnum, filter_td_map
from ius_time.utils import TaskTime, datetime_format, datetime_pst, ius_theme

# TODO: Make database location configurable
DEFAULT_DB_PATH = Path(__file__).parent.parent.resolve() / "ius-tasks.db"
DEFAULT_DB_ENGINE = create_engine(f"sqlite:///{DEFAULT_DB_PATH}")

class Status(StrEnum):
    ACTIVE = "Active"
    COMPLETE = "Complete"

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    start_time: datetime_pst = Field(default_factory=datetime_pst.now)
    end_time: datetime_pst | None = None
    total_time: timedelta | None = None
    category: str
    status: Status = Status.ACTIVE

class TaskManager:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_engine = create_engine(f"sqlite:///{db_path}")
        self.session: Session | None = None
        self.console = Console(theme=ius_theme)
        self.create_task_table()

    def create_task_table(self) -> bool:
        try:
            SQLModel.metadata.create_all(self.db_engine)
            return True
        except Exception as e:
            self.console.print(f"[error]Error creating task table: {e}")
            return False
    
    # START FUNCTIONS
    def start_task(self, task_name: str, category: str = "Misc"):
        try:
            with Session(self.db_engine) as session:
                task = Task(name=task_name, category=category)
                session.add(task)
                session.commit()
                session.refresh(task)
            self.console.print(f"Starting task [info]{task.name}[/] at [info]{task.start_time.strftime(datetime_format)}[/]")
        except Exception as e:
            self.console.print(f"[error]Could not start task [info]{task_name}[/info]! \n{e}[/error]")
            
    # END FUNCTIONS
    def _set_end_attributes(self, task: Task):
        task.end_time = datetime_pst.now()
        task.total_time = task.end_time - datetime_pst.from_datetime(task.start_time)
        task.status = Status.COMPLETE
        
    def _print_end_successful(self, task: Task):
        self.console.print(f"[success]Task [info]{task.name}[/info] ended after [info]{TaskTime(task.total_time.total_seconds())!s}[/info] :100:")       
    
    def end_task(self, task_name: str) -> bool:
        try:
            with Session(self.db_engine) as session:
                task: Task | None = session.exec(
                    select(Task).where(Task.name == task_name, Task.status == Status.ACTIVE)
                ).first()
                if task:
                    self._set_end_attributes(task)
                    session.commit()
                    session.refresh(task)
                    self._print_end_successful(task)
                    return True
                else:
                    self.console.print(f"[error]{task_name} is not an Active Task[/error]")
                    return False
        except Exception as e:
            self.console.print(f"[error]Could not end task [info]{task_name}[/info]: {e}[/error]")
            return False

    def end_last(self) -> bool:
        try:
            with Session(self.db_engine) as session:
                last_task_name = session.exec(
                    select(Task.name).where(
                        Task.start_time == (
                            select(func.max(Task.start_time))
                            .where(Task.status == Status.ACTIVE)
                            .scalar_subquery()
                        )
                    )
                ).first()
            if last_task_name:
                return self.end_task(last_task_name)
            else:
                self.console.print("[error]No active tasks to end![/error]")
                return False
        except Exception as e:
            self.console.print(f"[error]Could not end last task: {e}[/error]")
            return False
    
    def end_all_active(self) -> bool:
        try:
            with Session(self.db_engine) as session:
               active_tasks = session.exec(
                   select(Task).where(Task.status == Status.ACTIVE)
               ).all()
               for task in active_tasks:
                   self._set_end_attributes(task)
               session.commit()
            self.console.print(f"[success]Ended [info]{len(active_tasks)}[/info] active tasks at [info]{datetime_pst.now().strftime(datetime_format)}[/info]!")
            return True
        except Exception as e:
            self.console.print(f"[error]Could not end all tasks: {e}[/error]")
            return False
            
    # LIST FUNCTIONS
    def list_active(self, filter_: FilterEnum = FilterEnum.MONTH) -> list[Task]:
        expression = select(Task).where(Task.status == Status.ACTIVE)
        if filter_ != FilterEnum.NONE:
            filter_start_time = datetime_pst.now() - filter_td_map[filter_]
            expression = expression.where(Task.start_time >= filter_start_time)
        with Session(self.db_engine) as session:
            active_tasks = session.exec(expression).all()
            return list(active_tasks)
            
    def list_complete(self, filter_: FilterEnum = FilterEnum.MONTH) -> list[Task]:
        expression = select(Task).where(Task.status == Status.COMPLETE)
        if filter_ != FilterEnum.NONE:
            filter_start_time = datetime_pst.now() - filter_td_map[filter_]
            expression = expression.where(Task.start_time >= filter_start_time)
        with Session(self.db_engine) as session:
            complete_tasks = session.exec(expression).all()
            return list(complete_tasks)
    
    def list_all(self, filter_: FilterEnum = FilterEnum.MONTH) -> list[Task]:
        expression = select(Task)
        if filter_ != FilterEnum.NONE:
            filter_start_time = datetime_pst.now() - filter_td_map[filter_]
            expression = expression.where(Task.start_time >= filter_start_time)
        with Session(self.db_engine) as session:
            all_tasks = session.exec(expression).all()
            return list(all_tasks)
            
    # TOTAL FUNCTIONS
    def sum_task_times(self, filter_: FilterEnum = FilterEnum.MONTH, category: str | None = None) -> list[tuple[str, int]]:
        expression = select(Task.category, Task.total_time).where(Task.status == Status.COMPLETE)
        if category:
            expression = expression.where(Task.category == category)
        if filter_ != FilterEnum.NONE:
            filter_start_time = datetime_pst.now() - filter_td_map[filter_]
            expression = expression.where(Task.start_time >= filter_start_time)
        with Session(self.db_engine) as session:
            total_times: list[tuple[str, timedelta]] = session.exec(expression).all()
        # TODO: Use SQL 'GROUP BY' and 'SUM' to handle the logic
        sorted_total_times = sorted(total_times, key=lambda x: x[0])
        grouped_times = it.groupby(sorted_total_times, key=lambda x: x[0])
        results = [
            (group, sum(row[1].total_seconds() for row in rows))
            for group, rows in grouped_times
        ]
        return sorted(results, key=lambda x: x[1], reverse=True)