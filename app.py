import flet as ft

from config import get_config
from storage_http import HttpStorage
from ui.todo_app import TodoApp


def main(page: ft.Page):
    config = get_config()
    print("API URL:", config.api_url)
    page.title = "Семейный Todo-лист"
    page.padding = 16
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 720
    page.window.height = 900

    page.add(TodoApp(storage=HttpStorage(config.api_url)))


ft.run(main)
