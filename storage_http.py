from datetime import date, datetime
from typing import List, Optional

import httpx

from models import Task, User
from storage import Storage


class HttpStorage(Storage):
    def __init__(self, api_url: str, timeout: float = 10.0):
        self._api_url = api_url.rstrip("/")
        self._timeout = timeout
        self._token: Optional[str] = None

    def _headers(self) -> dict:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    def _request(self, method: str, path: str, json: dict = None) -> Optional[dict]:
        resp = httpx.request(
            method,
            self._api_url + path,
            json=json,
            headers=self._headers(),
            timeout=self._timeout,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"API error {resp.status_code}: {resp.text}")
        if not resp.content:
            return None
        data = resp.json()
        return data if isinstance(data, dict) else None

    def _list(self, method: str, path: str, json: dict = None) -> List[dict]:
        resp = httpx.request(
            method,
            self._api_url + path,
            json=json,
            headers=self._headers(),
            timeout=self._timeout,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"API error {resp.status_code}: {resp.text}")
        return resp.json()

    def authenticate(self, login: str, password: str) -> Optional[User]:
        resp = httpx.post(
            self._api_url + "/api/login",
            json={"login": login, "password": password},
            timeout=self._timeout,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        self._token = data["token"]
        u = data["user"]
        return User(id=u["id"], login=u["login"], name=u["name"], password_hash="")

    def get_user_by_login(self, login: str) -> Optional[User]:
        raise NotImplementedError

    def create_user(self, login: str, name: str, password_hash: str) -> User:
        raise NotImplementedError

    def list_users(self) -> List[User]:
        rows = self._list("GET", "/api/users")
        return [User(id=r["id"], login=r["login"], name=r["name"], password_hash="") for r in rows]

    def list_tasks(self, scope: str, user_id: int) -> List[Task]:
        rows = self._list("GET", f"/api/tasks?scope={scope}")
        return [self._row_to_task(r) for r in rows]

    def add_task(self, task: Task) -> Task:
        data = self._request("POST", "/api/tasks", json=self._task_in(task))
        task.id = data["id"]
        task.created_at = datetime.fromisoformat(data["created_at"])
        return task

    def update_task(self, task: Task) -> None:
        self._request("PUT", f"/api/tasks/{task.id}", json=self._task_in(task))

    def delete_task(self, task_id: int) -> None:
        self._request("DELETE", f"/api/tasks/{task_id}")

    def get_task(self, task_id: int) -> Optional[Task]:
        resp = httpx.get(
            self._api_url + f"/api/tasks?scope=family",
            headers=self._headers(),
            timeout=self._timeout,
        )
        if resp.status_code != 200:
            return None
        for r in resp.json():
            if r["id"] == task_id:
                return self._row_to_task(r)
        return None

    def create_token(self, user_id: int) -> str:
        raise NotImplementedError

    def get_user_by_token(self, token: str) -> Optional[User]:
        raise NotImplementedError

    def delete_token(self, token: str) -> None:
        self._request("POST", "/api/logout")

    @staticmethod
    def _row_to_task(row: dict) -> Task:
        due = None
        if row.get("due_date"):
            try:
                due = date.fromisoformat(row["due_date"])
            except ValueError:
                due = None
        return Task(
            id=row["id"],
            title=row["title"],
            scope=row["scope"],
            owner_id=row["owner_id"],
            assignee_id=row.get("assignee_id"),
            priority=row.get("priority", 0),
            due_date=due,
            completed=bool(row.get("completed", False)),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _task_in(task: Task) -> dict:
        return {
            "title": task.title,
            "scope": task.scope,
            "assignee_id": task.assignee_id,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed": task.completed,
        }