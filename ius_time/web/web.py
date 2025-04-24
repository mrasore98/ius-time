from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ius_time.db import DEFAULT_DB_PATH, TaskManager

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
