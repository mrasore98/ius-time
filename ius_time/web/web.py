from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from ius_time.db import DEFAULT_DB_PATH, Session, Status, Task, TaskManager

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

task_manager = TaskManager(DEFAULT_DB_PATH)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    active_tasks = task_manager.list_active()
    complete_tasks = task_manager.list_complete()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"active": active_tasks, "complete": complete_tasks},
    )


@app.post("/start")
async def start_task(request: Request):
    form_data = await request.form()
    name = form_data["new-task-name"]
    category = form_data["new-task-category"]
    task_manager.start_task(name, category)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    # with Session(task_manager.db_engine) as session:
    #     new_task = session.exec(
    #         select(Task).where(
    #             Task.name == name,
    #             Task.category == category,
    #             Task.status == Status.ACTIVE,
    #         )
    #     ).one()
    # return new_task.model_dump_json(exclude_none=True)


@app.get("/end/{task_name}", response_class=JSONResponse)
async def end_task(request: Request, task_name: str):
    task_manager.end_task(task_name)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    # with Session(task_manager.db_engine) as session:
    #     completed_task = session.exec(
    #         select(Task).where(Task.name == task_name, Task.status == Status.COMPLETE)
    #     ).one()
    # return completed_task.model_dump_json()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
