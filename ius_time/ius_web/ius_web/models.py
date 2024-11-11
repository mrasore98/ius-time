import reflex as rx

from ius_time.db import Status

class Tasks(rx.Model, table=True):
    name: str
    start_time: int
    end_time: int | None
    total_time: int | None
    category: str
    status: str
