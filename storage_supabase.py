from datetime import date, datetime
from typing import List, Optional

from models import SCOPE_PERSONAL, Task, User


class SupabaseStorage:
    def __init__(self, url: str, anon_key: str, service_key: str = ""):
        self._url = url
        self._anon_key = anon_key
        self._service_key = service_key
        self._client = self._build_client()

    def _build_client(self):
        try:
            from supabase import create_client
        except ImportError:
            raise RuntimeError(
                "Пакет supabase не установлен. Выполните: pip install supabase"
            )
        return create_client(self._url, self._anon_key)

    def _table(self, name: str):
        return self._client.table(name)

    def authenticate(self, login: str, password: str) -> Optional[User]:
        try:
            auth = self._client.auth.sign_in_with_password(
                {"email": login, "password": password}
            )
        except Exception:
            return None
        profile = (
            self._table("profiles")
            .select("*")
            .eq("id", auth.user.id)
            .single()
            .execute()
        )
        if not profile.data:
            return None
        return self._row_to_user(profile.data)

    def get_user_by_login(self, login: str) -> Optional[User]:
        result = (
            self._table("profiles").select("*").eq("email", login).execute()
        )
        if not result.data:
            return None
        return self._row_to_user(result.data[0])

    def create_user(self, login: str, name: str, password_hash: str) -> User:
        result = (
            self._table("profiles").insert({"email": login, "name": name}).execute()
        )
        row = result.data[0]
        return User(
            id=row["id"],
            login=row["email"],
            name=row["name"],
            password_hash=password_hash,
        )

    def list_users(self) -> List[User]:
        result = self._table("profiles").select("*").order("name").execute()
        return [self._row_to_user(r) for r in (result.data or [])]

    def list_tasks(self, scope: str, user_id: int) -> List[Task]:
        user_id = str(user_id)
        query = self._table("tasks").select("*").eq("scope", scope)
        if scope == SCOPE_PERSONAL:
            query = query.eq("owner_id", user_id)
        result = query.execute()
        return [self._row_to_task(r) for r in (result.data or [])]

    def add_task(self, task: Task) -> Task:
        data = {
            "title": task.title,
            "scope": task.scope,
            "owner_id": str(task.owner_id),
            "assignee_id": str(task.assignee_id) if task.assignee_id else None,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed": task.completed,
        }
        result = self._table("tasks").insert(data).execute()
        task.id = result.data[0]["id"]
        return task

    def update_task(self, task: Task) -> None:
        data = {
            "title": task.title,
            "scope": task.scope,
            "owner_id": str(task.owner_id),
            "assignee_id": str(task.assignee_id) if task.assignee_id else None,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed": task.completed,
        }
        self._table("tasks").update(data).eq("id", task.id).execute()

    def delete_task(self, task_id: int) -> None:
        self._table("tasks").delete().eq("id", task_id).execute()

    @staticmethod
    def _row_to_user(row: dict) -> User:
        return User(
            id=row["id"],
            login=row["email"],
            name=row["name"],
            password_hash="",
        )

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
            created_at=datetime.now(),
        )