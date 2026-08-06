from abc import ABC, abstractmethod
from typing import List, Optional

from models import Task, User


class Storage(ABC):
    @abstractmethod
    def get_user_by_login(self, login: str) -> Optional[User]:
        ...

    @abstractmethod
    def authenticate(self, login: str, password: str) -> Optional[User]:
        ...

    @abstractmethod
    def create_user(self, login: str, name: str, password_hash: str) -> User:
        ...

    @abstractmethod
    def list_users(self) -> List[User]:
        ...

    @abstractmethod
    def list_tasks(self, scope: str, user_id: int) -> List[Task]:
        ...

    @abstractmethod
    def add_task(self, task: Task) -> Task:
        ...

    @abstractmethod
    def update_task(self, task: Task) -> None:
        ...

    @abstractmethod
    def delete_task(self, task_id: int) -> None:
        ...

    @abstractmethod
    def get_task(self, task_id: int) -> Optional[Task]:
        ...

    @abstractmethod
    def create_token(self, user_id: int) -> str:
        ...

    @abstractmethod
    def get_user_by_token(self, token: str) -> Optional[User]:
        ...

    @abstractmethod
    def delete_token(self, token: str) -> None:
        ...