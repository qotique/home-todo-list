import flet as ft
from flet.controls.base_control import skip_field

from models import User
from storage import Storage

from .login_view import LoginView
from .main_view import MainView


@ft.control
class TodoApp(ft.Column):
    storage: Storage = skip_field()

    def init(self):
        self.expand = True
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.current_user: User | None = None
        self._show_login()

    def _show_login(self):
        self.current_user = None
        self.login_view = LoginView(storage=self.storage, on_login=self.on_login)
        self.controls = [self.login_view]
        self.spacing = 0

    def on_login(self, user: User):
        self.current_user = user
        self.main_view = MainView(
            storage=self.storage, user=user, on_logout=self.on_logout
        )
        self.controls = [self.main_view]
        self.update()

    def on_logout(self):
        self._show_login()
        self.update()