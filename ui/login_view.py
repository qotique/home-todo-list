from dataclasses import field
from typing import Callable

import flet as ft

from auth import verify_password
from models import User
from storage import Storage


@ft.control
class LoginView(ft.Column):
    storage: Storage = None
    on_login: Callable[[User], None] = field(default=lambda user: None)

    def init(self):
        self.width = 380
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.login_field = ft.TextField(
            label="Логин", autofocus=True, on_submit=self.login_clicked
        )
        self.password_field = ft.TextField(
            label="Пароль",
            password=True,
            can_reveal_password=True,
            on_submit=self.login_clicked,
        )
        self.error_text = ft.Text(
            value="", visible=False, color=ft.Colors.RED, size=13
        )

        self.controls = [
            ft.Icon(ft.Icons.CHECKLIST, size=56, color=ft.Colors.PRIMARY),
            ft.Text(
                "Семейный Todo-лист",
                style=ft.TextStyle(size=22, weight=ft.FontWeight.BOLD),
            ),
            self.login_field,
            self.password_field,
            ft.FilledButton(
                content=ft.Text("Войти"),
                width=380,
                on_click=self.login_clicked,
            ),
            self.error_text,
        ]

    def login_clicked(self, e):
        login = self.login_field.value.strip()
        user = self.storage.get_user_by_login(login) if login else None
        if user is None or not verify_password(
            self.password_field.value, user.password_hash
        ):
            self.error_text.value = "Неверный логин или пароль"
            self.error_text.visible = True
            self.update()
            return
        self.on_login(user)