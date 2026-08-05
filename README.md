# Family Todo List

Семейный todo-лист на Flet: задачи разделены на **личные** и **семейные**.
Платформы: Web (VPS), нативное Android-приложение, iOS (PWA).

## Возможности
- Логин с паролем
- Вкладки «Семейные» / «Личные»
- Приоритеты, дедлайны, назначение ответственного
- Фильтры (all / active / completed)
- Хранилище: SQLite или Supabase (интерфейс `Storage`)

## Структура проекта
- `app.py` — точка входа приложения
- `models.py` — модели `User`, `Task`
- `storage.py` — абстрактный интерфейс хранилища
- `storage_sqlite.py` — реализация на SQLite
- `storage_supabase.py` — реализация на Supabase
- `ui/` — Flet-контролы (вход, навигация, список задач)
- `.github/workflows/` — GitHub Actions (сборка Android APK)