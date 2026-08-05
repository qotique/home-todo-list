import sqlite3
from datetime import date, datetime
from typing import List, Optional

from auth import verify_password
from models import SCOPE_PERSONAL, Task, User
from storage import Storage

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    login         TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    scope       TEXT NOT NULL,
    owner_id    INTEGER NOT NULL REFERENCES users(id),
    assignee_id INTEGER REFERENCES users(id),
    priority    INTEGER NOT NULL DEFAULT 0,
    due_date    TEXT,
    completed   INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_scope ON tasks(scope);
CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks(owner_id);
"""


class SQLiteStorage(Storage):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def get_user_by_login(self, login: str) -> Optional[User]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE login = ?", (login,)
            ).fetchone()
        return self._row_to_user(row) if row else None

    def authenticate(self, login: str, password: str) -> Optional[User]:
        user = self.get_user_by_login(login)
        if user is None or not verify_password(password, user.password_hash):
            return None
        return user

    def create_user(self, login: str, name: str, password_hash: str) -> User:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO users (login, name, password_hash) VALUES (?, ?, ?)",
                (login, name, password_hash),
            )
            user_id = cur.lastrowid
        return User(id=user_id, login=login, name=name, password_hash=password_hash)

    def list_users(self) -> List[User]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY name").fetchall()
        return [self._row_to_user(r) for r in rows]

    def list_tasks(self, scope: str, user_id: int) -> List[Task]:
        with self._connect() as conn:
            if scope == SCOPE_PERSONAL:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE scope = ? AND owner_id = ?",
                    (scope, user_id),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE scope = ?", (scope,)
                ).fetchall()
        return [self._row_to_task(r) for r in rows]

    def add_task(self, task: Task) -> Task:
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO tasks
                   (title, scope, owner_id, assignee_id, priority, due_date, completed, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    task.title,
                    task.scope,
                    task.owner_id,
                    task.assignee_id,
                    task.priority,
                    task.due_date.isoformat() if task.due_date else None,
                    1 if task.completed else 0,
                    task.created_at.isoformat(),
                ),
            )
            task.id = cur.lastrowid
        return task

    def update_task(self, task: Task) -> None:
        with self._connect() as conn:
            conn.execute(
                """UPDATE tasks SET
                     title=?, scope=?, owner_id=?, assignee_id=?, priority=?,
                     due_date=?, completed=?
                   WHERE id=?""",
                (
                    task.title,
                    task.scope,
                    task.owner_id,
                    task.assignee_id,
                    task.priority,
                    task.due_date.isoformat() if task.due_date else None,
                    1 if task.completed else 0,
                    task.id,
                ),
            )

    def delete_task(self, task_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    @staticmethod
    def _row_to_user(row: sqlite3.Row) -> User:
        return User(
            id=row["id"],
            login=row["login"],
            name=row["name"],
            password_hash=row["password_hash"],
        )

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            scope=row["scope"],
            owner_id=row["owner_id"],
            assignee_id=row["assignee_id"],
            priority=row["priority"],
            due_date=(
                date.fromisoformat(row["due_date"]) if row["due_date"] else None
            ),
            completed=bool(row["completed"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
