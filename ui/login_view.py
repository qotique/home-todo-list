from dataclasses import field
from typing import Callable

import flet as ft
import httpx
from flet.controls.base_control import skip_field

from models import User
from storage import Storage


@ft.control
class LoginView(ft.Column):
    storage: Storage = skip_field()
    on_login: Callable[[User], None] = field(
        default=lambda user: None, metadata={"skip": True}
    )

    def init(self):
        self.expand = True
        self.spacing = 0

        self.login_field = ft.TextField(
            label="Логин", width=380, autofocus=True, on_submit=self.login_clicked
        )
        self.password_field = ft.TextField(
            label="Пароль",
            width=380,
            password=True,
            can_reveal_password=True,
            on_submit=self.login_clicked,
        )
        self.error_text = ft.Text(
            value="", visible=False, color=ft.Colors.RED, size=13
        )

        form = ft.Column(
            width=380,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
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
            ],
        )

        self.controls = [
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=form,
            )
        ]

    def login_clicked(self, e):
        login = self.login_field.value.strip()
        try:
            user = (
                self.storage.authenticate(login, self.password_field.value)
                if login
                else None
            )
        except httpx.HTTPError:
            url = getattr(self.storage, "api_url", "")
            self.error_text.value = f"Не удалось подключиться к {url}"
            self.error_text.visible = True
            self.update()
            return
        if user is None:
            self.error_text.value = "Неверный логин или пароль"
            self.error_text.visible = True
            self.update()
            return
        self.on_login(user)