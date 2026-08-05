from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

SCOPE_PERSONAL = "personal"
SCOPE_FAMILY = "family"

PRIORITY_LOW = 0
PRIORITY_MEDIUM = 1
PRIORITY_HIGH = 2


@dataclass
class User:
    id: int
    login: str
    name: str
    password_hash: str


@dataclass
class Task:
    title: str
    scope: str
    owner_id: int
    assignee_id: Optional[int] = None
    priority: int = PRIORITY_LOW
    due_date: Optional[date] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
