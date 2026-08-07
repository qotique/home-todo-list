from dataclasses import field
from datetime import date
from typing import Callable

import flet as ft
from flet.controls.base_control import skip_field

from models import SCOPE_FAMILY, SCOPE_PERSONAL, Task, User
from storage import Storage

from .task_dialog import TaskDialog
from .task_item import TaskItem

_FILTERS = ["all", "active", "completed"]


@ft.control
class MainView(ft.Column):
    storage: Storage = skip_field()
    user: User = skip_field()
    on_logout: Callable[[], None] = field(
        default=lambda: None, metadata={"skip": True}
    )

    def init(self):
        self.scope = SCOPE_FAMILY
        self.filter = "all"
        self.expand = True
        self.spacing = 8

        self.scope_bar = ft.TabBar(
            tab_alignment=ft.TabAlignment.CENTER,
            tabs=[ft.Tab(label="Семейные"), ft.Tab(label="Личные")],
        )
        self.scope_tabs = ft.Tabs(
            length=2,
            selected_index=0,
            on_change=self.scope_changed,
            content=self.scope_bar,
        )

        self.filter_bar = ft.TabBar(
            tab_alignment=ft.TabAlignment.CENTER,
            tabs=[ft.Tab(label="Все"), ft.Tab(label="Активные"), ft.Tab(label="Завершённые")],
        )
        self.filter_tabs = ft.Tabs(
            length=3,
            selected_index=0,
            on_change=self.filter_changed,
            content=self.filter_bar,
        )

        self.remaining_text = ft.Text("", size=13, color=ft.Colors.GREY_700)
        self.clear_completed_btn = ft.TextButton(
            content=ft.Text("Очистить завершённые"),
            visible=False,
            on_click=self.clear_completed,
        )
        self.group_footer = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[self.remaining_text, self.clear_completed_btn],
        )

        self.tasks_view = ft.Column(spacing=8, expand=True, scroll=ft.ScrollMode.AUTO)
        self.fab = ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=self.add_clicked)

        self.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Семейный Todo-лист",
                            style=ft.TextStyle(size=22, weight=ft.FontWeight.BOLD)),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.CircleAvatar(
                                content=ft.Text(self.user.name[:1], size=16)
                            ),
                            ft.Text(self.user.name, weight=ft.FontWeight.W_600),
                            ft.IconButton(
                                icon=ft.Icons.LOGOUT,
                                tooltip="Выйти",
                                on_click=self.logout_clicked,
                            ),
                        ],
                    ),
                ],
            ),
            self.scope_tabs,
            self.filter_tabs,
            self.tasks_view,
            self.group_footer,
            self.fab,
        ]

        self.reload_tasks()

    def reload_tasks(self):
        tasks = self.storage.list_tasks(self.scope, self.user.id)
        tasks.sort(key=lambda t: (-t.priority, t.due_date or date.max))
        self.tasks_view.controls.clear()
        users = self.storage.list_users()
        for t in tasks:
            self.tasks_view.controls.append(
                TaskItem(
                    task=t,
                    storage=self.storage,
                    scope=self.scope,
                    users=users,
                    on_changed=self.reload_tasks,
                )
            )

    def scope_changed(self, e):
        self.scope = (
            SCOPE_FAMILY if self.scope_tabs.selected_index == 0 else SCOPE_PERSONAL
        )
        self.reload_tasks()
        self.update()

    def filter_changed(self, e):
        self.filter = _FILTERS[self.filter_tabs.selected_index]
        self.update()

    def before_update(self):
        for item in self.tasks_view.controls:
            item.visible = (
                self.filter == "all"
                or (self.filter == "active" and not item.task.completed)
                or (self.filter == "completed" and item.task.completed)
            )
        remaining = sum(
            1 for t in self.tasks_view.controls if not t.task.completed
        )
        self.remaining_text.value = f"Осталось задач: {remaining}"
        self.clear_completed_btn.visible = any(
            t.task.completed for t in self.tasks_view.controls
        )

    def add_clicked(self, e):
        new_task = Task(
            title="",
            scope=self.scope,
            owner_id=self.user.id,
            assignee_id=self.user.id if self.scope == SCOPE_PERSONAL else None,
        )
        dialog = TaskDialog(
            task=new_task,
            storage=self.storage,
            scope=self.scope,
            users=self.storage.list_users(),
            title_text="Новая задача",
            on_saved=self.reload_tasks,
        )
        self.page.show_dialog(dialog)

    def clear_completed(self, e):
        for t in list(self.tasks_view.controls):
            if t.task.completed and t.task.id is not None:
                self.storage.delete_task(t.task.id)
        self.reload_tasks()
        self.update()

    def logout_clicked(self, e):
        self.on_logout()