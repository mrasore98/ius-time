import reflex as rx

from ius_time.db import DB_PATH

config = rx.Config(
    app_name="ius_web",
    db_url=f"sqlite:///{DB_PATH}"
)
