from datetime import date, datetime
from typing import List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from config import get_config
from models import PRIORITY_LOW, Task, User
from storage import Storage
from storage_sqlite import SQLiteStorage

app = FastAPI(title="Family Todo API")
_bearer = HTTPBearer(auto_error=False)

_config = get_config()
_storage: Storage = SQLiteStorage(_config.db_path)


def _user_out(user: User) -> dict:
    return {"id": user.id, "login": user.login, "name": user.name}


def _task_out(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "scope": task.scope,
        "owner_id": task.owner_id,
        "assignee_id": task.assignee_id,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
    }


def current_user(
    cred: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> User:
    if cred is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    user = _storage.get_user_by_token(cred.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Неверный или истёкший токен")
    return user


def check_task_access(task: Task, user: User) -> None:
    if task.owner_id != user.id and task.scope != "family":
        raise HTTPException(status_code=403, detail="Нет доступа к задаче")


class LoginIn(BaseModel):
    login: str
    password: str


class LoginOut(BaseModel):
    token: str
    user: dict


class TaskIn(BaseModel):
    title: str
    scope: str
    assignee_id: Optional[int] = None
    priority: int = PRIORITY_LOW
    due_date: Optional[str] = None
    completed: bool = False


@app.post("/api/login", response_model=LoginOut)
def login(body: LoginIn):
    user = _storage.authenticate(body.login, body.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    token = _storage.create_token(user.id)
    return {"token": token, "user": _user_out(user)}


@app.post("/api/logout")
def logout(
    cred: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    user: User = Depends(current_user),
):
    _storage.delete_token(cred.credentials)
    return {"ok": True}


@app.get("/api/users")
def list_users(_: User = Depends(current_user)) -> List[dict]:
    return [_user_out(u) for u in _storage.list_users()]


@app.get("/api/tasks")
def list_tasks(
    scope: str, user: User = Depends(current_user)
) -> List[dict]:
    tasks = _storage.list_tasks(scope, user.id)
    tasks.sort(key=lambda t: (-t.priority, t.due_date or date.max))
    return [_task_out(t) for t in tasks]


@app.post("/api/tasks")
def add_task(body: TaskIn, user: User = Depends(current_user)) -> dict:
    if body.scope not in ("personal", "family"):
        raise HTTPException(status_code=400, detail="Неверная область видимости")
    task = Task(
        title=body.title,
        scope=body.scope,
        owner_id=user.id,
        assignee_id=body.assignee_id,
        priority=body.priority,
        due_date=_parse_date(body.due_date),
        completed=body.completed,
    )
    return _task_out(_storage.add_task(task))


@app.put("/api/tasks/{task_id}")
def update_task(
    task_id: int, body: TaskIn, user: User = Depends(current_user)
) -> dict:
    task = _storage.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    check_task_access(task, user)
    task.title = body.title
    task.scope = body.scope
    task.assignee_id = body.assignee_id
    task.priority = body.priority
    task.due_date = _parse_date(body.due_date)
    task.completed = body.completed
    _storage.update_task(task)
    return _task_out(task)


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, user: User = Depends(current_user)) -> dict:
    task = _storage.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    check_task_access(task, user)
    _storage.delete_task(task_id)
    return {"ok": True}


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверная дата")


if __name__ == "__main__":
    uvicorn.run(app, host=_config.host, port=_config.port)