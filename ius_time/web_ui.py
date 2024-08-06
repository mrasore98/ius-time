from fasthtml import common as fh

from ius_time.db import DB_PATH

app, rt, tasks, Task = fh.fast_app(db_file=DB_PATH, hdrs=fh.picolink,
                                   id=int,
                                   name=str,
                                   start_time=float,
                                   end_time=float,
                                   total_time=float,
                                   categorty=str,
                                   status=str,
                                   pk="id")


@rt("/")
def get():
    return fh.Titled("IUS Time",
                     fh.Div(fh.P("Hello, World")))


def run():
    fh.serve(appname=".", port=5001)
