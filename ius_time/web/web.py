import urllib.parse as urlp

from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from ius_time.db import DEFAULT_DB_PATH, Session, Status, Task, TaskManager

app = FastAPI()
templates = Jinja2Templates(directory="templates")
task_manager = TaskManager(DEFAULT_DB_PATH)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, message: str = ""):
    active_tasks = task_manager.list_active()
    complete_tasks = task_manager.list_complete()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "active": active_tasks,
            "complete": complete_tasks,
            "message": urlp.unquote(message),
        },
    )


@app.post("/start")
async def start_task(request: Request):
    form_data = await request.form()
    name = form_data["new-task-name"]
    if name == "":
        return RedirectResponse(f"/?message={urlp.quote('Task must have a name')}")
    category = form_data["new-task-category"]
    try:
        task_manager.start_task(name, category)
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        return RedirectResponse(
            f"/?message={urlp.quote(str(e))}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.get("/end/{task_name}", response_class=JSONResponse)
async def end_task(request: Request, task_name: str):
    try:
        task_manager.end_task(task_name)
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        return RedirectResponse(
            f"/?message={urlp.quote(str(e))}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
