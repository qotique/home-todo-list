from dataclasses import field
from typing import Callable

import flet as ft
from flet.controls.base_control import skip_field

from models import SCOPE_FAMILY, Task, User
from storage import Storage

from .formatters import _make_meta, task_assignee
from .task_dialog import TaskDialog


@ft.control
class TaskItem(ft.Column):
    task: Task = skip_field()
    storage: Storage = skip_field()
    scope: str = ""
    users: list[User] = field(default_factory=list, metadata={"skip": True})
    on_changed: Callable[[], None] = field(
        default=lambda: None, metadata={"skip": True}
    )

    def init(self):
        self.spacing = 0
        assignee_name = (
            task_assignee(self.task.assignee_id, self.users)
            if self.scope == SCOPE_FAMILY
            else None
        )

        self.checkbox = ft.Checkbox(
            value=self.task.completed, on_change=self.status_changed
        )

        title_style = ft.TextStyle(
            weight=ft.FontWeight.W_500,
            decoration=(
                ft.TextDecoration.LINE_THROUGH if self.task.completed else None
            ),
            color=(
                ft.Colors.GREY_500 if self.task.completed else ft.Colors.ON_SURFACE
            ),
        )
        title = ft.Text(self.task.title, size=16, style=title_style)

        body_controls = [title]
        if self.task.description:
            body_controls.append(
                ft.Text(
                    self.task.description,
                    size=13,
                    color=ft.Colors.GREY_700,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
            )
        body_controls.append(
            _make_meta(
                self.task.priority,
                self.task.due_date,
                assignee_name,
            )
        )

        self.controls = [
            ft.Card(
                content=ft.Container(
                    padding=ft.padding.Padding(right=8, left=8, top=4, bottom=4),
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.checkbox,
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=body_controls,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip="Изменить",
                                on_click=self.edit_clicked,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Удалить",
                                on_click=self.delete_clicked,
                            ),
                        ],
                    ),
                )
            )
        ]

    def status_changed(self, e):
        self.task.completed = self.checkbox.value
        self.storage.update_task(self.task)
        self.on_changed()

    def edit_clicked(self, e):
        dialog = TaskDialog(
            task=self.task,
            storage=self.storage,
            scope=self.scope,
            users=self.users,
            title_text="Изменить задачу",
            on_saved=self.on_changed,
        )
        self.page.show_dialog(dialog)

    def delete_clicked(self, e):
        if self.task.id is not None:
            self.storage.delete_task(self.task.id)
        self.on_changed()