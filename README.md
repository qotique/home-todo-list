# Family Todo List

Семейный todo-лист на Flet: задачи разделены на **личные** и **семейные**.
Платформы: Web (VPS), нативное Android-приложение, iOS (PWA).

## Возможности
- Логин с паролем
- Вкладки «Семейные» / «Личные»
- Приоритеты, дедлайны, назначение ответственного
- Фильтры (Все / Активные / Завершённые)
- Хранилище: SQLite, Supabase или собственный API (интерфейс `Storage`)

## Архитектура

Клиент-сервер: на сервере (VPS) работает REST API, отдельные клиенты
(web, Android, iOS PWA) общаются с ним по HTTP.

```
Браузер (web) ─┐
Android ───────┼── HTTP ──► FastAPI (server.py) ──► SQLite
iOS (PWA) ─────┘            (session-токены)
```

Клиенты используют общий интерфейс `Storage`; реализация `HttpStorage`
(`storage_http.py`) ходит к API. В офлайн/локальном режиме возможны
`SQLiteStorage` и `SupabaseStorage` без сервера.

## Структура проекта
- `app.py` — точка входа Flet-клиента (выбор реализации по `STORAGE_BACKEND`)
- `server.py` — REST API (FastAPI): login/logout по токенам, CRUD задач
- `models.py` — модели `User`, `Task`
- `storage.py` — абстрактный интерфейс хранилища (включая сессии/токены)
- `storage_sqlite.py` — SQLite: данные + сессии
- `storage_http.py` — HTTP-клиент для `STORAGE_BACKEND=api`
- `storage_supabase.py` — реализация на Supabase
- `auth.py` — хэширование паролей (pbkdf2)
- `seed_users.py` — CLI добавления пользователей
- `ui/` — Flet-контролы (вход, навигация, список задач, диалог задачи)
- `supabase/schema.sql` — схема и RLS для Supabase
- `deploy/api.service`, `deploy/web.service` — юниты systemd для VPS
- `.github/workflows/build.yml` — сборка Android APK

## Запуск локально (SQLite, без сервера)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed_users.py mama Мама --password mypass
python seed_users.py papa Папа --password mypass
python app.py
```

## Запуск клиент-сервер локально

```bash
# терминал 1 — API
STORAGE_BACKEND=sqlite python seed_users.py mama Мама --password mypass
python server.py

# терминал 2 — клиент (web или десктоп)
STORAGE_BACKEND=api API_URL=http://127.0.0.1:8000 flet run app.py
```

## Деплой на VPS (клиент-сервер)

1. Скопируйте код в `/opt/home-todo-list`, установите зависимости в venv.

2. Создайте `/opt/home-todo-list/.env`:
   - `STORAGE_BACKEND=api`
   - `API_URL=http://127.0.0.1:8000`
   - `DB_PATH=/opt/home-todo-list/family_todo.db`
   - `HOST=0.0.0.0`, `PORT=8000`

3. Создайте пользователей: `seed_users.py` (выполняется на сервере от владельца БД).

4. Установите службы:

```bash
sudo cp deploy/api.service /etc/systemd/system/family-todo-api.service
sudo cp deploy/web.service /etc/systemd/system/family-todo-web.service
sudo systemctl daemon-reload
sudo systemctl enable --now family-todo-api family-todo-web
```

- API: порт `8000` (`/api/login`, `/api/tasks`, ...).
- Web-клиент: порт `8550`.
Логи: `journalctl -u family-todo-api -f`, `journalctl -u family-todo-web -f`.

## Android

Сборка APK выполняется в GitHub Actions (`.github/workflows/build.yml`).
Перейдите в **Actions** → «Build Android APK» → **Run workflow**, затем скачайте
артефакт `home-todo-list-apk`. Нативное приложение использует
`STORAGE_BACKEND=api` с `API_URL` вашего VPS (через CI-секреты или `.env`).

## iOS (PWA)

Откройте web-версию `http://<IP-адрес-VPS>:8550` в Safari на iPhone/iPad и
выберите «На главный экран» — получите полноэкранное приложение.

## Supabase

Альтернативный режим без собственного сервера: клиенты ходят напрямую в
Supabase. Выполните `supabase/schema.sql`, создайте пользователей в Auth,
пропишите `STORAGE_BACKEND=supabase`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`
(RLS) или `SUPABASE_SERVICE_KEY` (web/VPS).
