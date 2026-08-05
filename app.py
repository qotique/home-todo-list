import flet as ft

from config import get_config
from storage_sqlite import SQLiteStorage
from ui.todo_app import TodoApp


def main(page: ft.Page):
    config = get_config()
    storage = SQLiteStorage(config.db_path)

    page.title = "Семейный Todo-лист"
    page.padding = 16
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 720
    page.window.height = 900

    page.add(TodoApp(storage))


ft.run(main)