from abc import ABC, abstractmethod
from typing import List, Optional

from models import Task, User


class Storage(ABC):
    """Абстрактный интерфейс хранилища.

    Реализации: SQLiteStorage (локально / web на VPS) и SupabaseStorage (облако / нативно).
    """

    # ---------------- Пользователи ----------------
    @abstractmethod
    def get_user_by_login(self, login: str) -> Optional[User]:
        """Вернуть пользователя по логину или None."""

    @abstractmethod
    def create_user(self, login: str, name: str, password_hash: str) -> User:
        """Создать пользователя и вернуть его."""

    @abstractmethod
    def list_users(self) -> List[User]:
        """Список всех пользователей семьи (для выбора ответственного)."""

    # ---------------- Задачи ----------------
    @abstractmethod
    def list_tasks(self, scope: str, user_id: int) -> List[Task]:
        """Задачи по области видимости. scope="personal" — только задачи user_id,
        scope="family" — все семейные задачи."""

    @abstractmethod
    def add_task(self, task: Task) -> Task:
        """Создать задачу и вернуть её с заполненным id."""

    @abstractmethod
    def update_task(self, task: Task) -> None:
        """Сохранить изменения задачи."""

    @abstractmethod
    def delete_task(self, task_id: int) -> None:
        """Удалить задачу по id."""