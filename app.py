import flet as ft

from config import get_config
from storage import Storage
from storage_sqlite import SQLiteStorage
from ui.todo_app import TodoApp


def build_storage() -> Storage:
    config = get_config()
    if config.storage_backend == "supabase":
        from storage_supabase import SupabaseStorage

        return SupabaseStorage(
            url=config.supabase_url,
            anon_key=config.supabase_anon_key,
            service_key=config.supabase_service_key,
        )
    return SQLiteStorage(config.db_path)


def main(page: ft.Page):
    page.title = "Семейный Todo-лист"
    page.padding = 16
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 720
    page.window.height = 900

    page.add(TodoApp(storage=build_storage()))


ft.run(main)