from dataclasses import field
from datetime import date, datetime, timedelta
from typing import Callable

import flet as ft

from models import PRIORITY_HIGH, PRIORITY_LOW, PRIORITY_MEDIUM, SCOPE_FAMILY, Task, User
from storage import Storage

from .formatters import format_date


@ft.control
class TaskDialog(ft.AlertDialog):
    task: Task = None
    storage: Storage = None
    scope: str = ""
    users: list[User] = field(default_factory=list)
    title_text: str = "Задача"
    on_saved: Callable[[], None] = field(default=lambda: None)

    def init(self):
        self.title = ft.Text(self.title_text)

        self.name = ft.TextField(
            label="Задача", value=self.task.title, autofocus=True
        )
        self.priority = ft.SegmentedButton(
            allow_empty_selection=False,
            selected=[str(self.task.priority)],
            segments=[
                ft.Segment(value=str(PRIORITY_LOW), label=ft.Text("Низкий")),
                ft.Segment(value=str(PRIORITY_MEDIUM), label=ft.Text("Средний")),
                ft.Segment(value=str(PRIORITY_HIGH), label=ft.Text("Высокий")),
            ],
        )

        self.date_picker = ft.DatePicker(
            value=self.task.due_date,
            first_date=datetime.now() - timedelta(days=365),
            last_date=datetime.now() + timedelta(days=3650),
            current_date=self.task.due_date or datetime.now(),
            on_change=self.date_changed,
        )
        self.due_button = ft.OutlinedButton(
            content=ft.Text(self._due_text()),
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=self.open_date_picker,
        )

        fields = [
            self.name,
            ft.Text("Приоритет", size=13, color=ft.Colors.GREY_700),
            self.priority,
            ft.Text("Срок", size=13, color=ft.Colors.GREY_700),
            self.due_button,
        ]

        self.error_text = ft.Text(value="", visible=False, color=ft.Colors.RED, size=13)

        if self.scope == SCOPE_FAMILY:
            options = []
            for u in self.users:
                options.append(
                    ft.DropdownOption(key=str(u.id), content=ft.Text(u.name))
                )
            self.assignee = ft.Dropdown(
                label="Ответственный",
                options=options,
                value=str(self.task.assignee_id) if self.task.assignee_id else None,
            )
            fields.append(self.assignee)

        fields.append(self.error_text)

        self.content = ft.Column(width=380, spacing=8, controls=fields)
        self.actions = [
            ft.TextButton("Отмена", on_click=self.cancel),
            ft.FilledButton(content=ft.Text("Сохранить"), on_click=self.save),
        ]

    def _due_text(self) -> str:
        if self.task.due_date is None:
            return "Срок: не задан"
        return "Срок: " + format_date(self.task.due_date)

    def open_date_picker(self, e):
        self.page.show_dialog(self.date_picker)

    def date_changed(self, e):
        value = self.date_picker.value
        if isinstance(value, datetime):
            self.task.due_date = value.date()
        elif isinstance(value, date):
            self.task.due_date = value
        else:
            self.task.due_date = None
        self.due_button.text = self._due_text()
        self.update()

    def save(self, e):
        title = self.name.value.strip()
        if not title:
            self.error_text.value = "Название не может быть пустым"
            self.error_text.visible = True
            self.update()
            return

        self.task.title = title
        if self.priority.selected:
            self.task.priority = int(self.priority.selected[0])
        if self.scope == SCOPE_FAMILY and self.assignee.value is not None:
            self.task.assignee_id = int(self.assignee.value)

        if self.task.id is None:
            self.storage.add_task(self.task)
        else:
            self.storage.update_task(self.task)

        self.on_saved()
        self.open = False
        self.update()

    def cancel(self, e):
        self.open = False
        self.update()