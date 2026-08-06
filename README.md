# Family Todo List

Семейный todo-лист на Flet: задачи разделены на **личные** и **семейные**.
Платформы: Web (VPS), нативное Android-приложение, iOS (PWA).

## Возможности
- Логин с паролем
- Вкладки «Семейные» / «Личные»
- Приоритеты, дедлайны, назначение ответственного
- Фильтры (Все / Активные / Завершённые)
- Клиент-сервер: клиенты ходят к REST API, база живёт на сервере (SQLite сейчас)

## Архитектура

```
Браузер (web) ─┐
Android ───────┼── HTTP ──► FastAPI (server.py) ──► SQLite (DB_BACKEND)
iOS (PWA) ─────┘            (session-токены)
```

- **Сервер** (`server.py`) — REST API: логин по токенам, CRUD задач. Выбор базы
  только здесь, через `DB_BACKEND` (сейчас `sqlite`).
- **Клиент** (`app.py`) — всегда использует `HttpStorage` и ходит к серверу по
  `API_URL`. Никакого локального хранилища у клиента нет.

## Структура проекта
- `app.py` — точка входа Flet-клиента (всегда `HttpStorage(API_URL)`)
- `server.py` — REST API (FastAPI): login/logout по токенам, CRUD задач, выбор БД
- `models.py` — модели `User`, `Task`
- `storage.py` — абстрактный интерфейс хранилища (включая сессии/токены)
- `storage_sqlite.py` — SQLite: данные + сессии
- `storage_http.py` — HTTP-клиент (используется приложением)
- `storage_supabase.py` — Supabase как база сервера (заготовка для `DB_BACKEND=supabase`)
- `auth.py` — хэширование паролей (pbkdf2)
- `seed_users.py` — CLI добавления пользователей (на сервере)
- `ui/` — Flet-контролы (вход, навигация, список задач, диалог задачи)
- `supabase/schema.sql` — схема и RLS для Supabase
- `deploy/api.service`, `deploy/web.service` — юниты systemd для VPS
- `.github/workflows/build.yml` — сборка Android APK

## Переменные окружения (.env)

Сервер (`server.py`, `seed_users.py`):
- `DB_BACKEND=sqlite` — какая база у сервера (sqlite сейчас)
- `DB_PATH=family_todo.db`
- `HOST=0.0.0.0`, `PORT=8000`
- (опционально при `DB_BACKEND=supabase`) `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_ANON_KEY`

Клиент (`app.py`):
- `API_URL=http://127.0.0.1:8000` — адрес API-сервера

## Запуск клиент-сервер локально

```bash
# терминал 1 — сервер: создаём пользователей и поднимаем API
python seed_users.py mama Мама --password mypass
python server.py

# терминал 2 — клиент (web или десктоп)
API_URL=http://127.0.0.1:8000 flet run app.py
```

Войти в приложение можно под `mama` / паролем, созданным выше.

## Деплой на VPS

1. Скопируйте код в `/opt/home-todo-list`, установите зависимости в venv.

2. Создайте `/opt/home-todo-list/.env`:
   - `DB_BACKEND=sqlite`
   - `DB_PATH=/opt/home-todo-list/family_todo.db`
   - `HOST=0.0.0.0`, `PORT=8000`
   - `API_URL=http://127.0.0.1:8000`

3. Создайте пользователей на сервере: `seed_users.py` (от владельца БД).

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
артефакт `home-todo-list-apk`. Нативное приложение использует `API_URL` вашего
VPS (через CI-секреты или `.env`).

## iOS (PWA)

Откройте web-версию `http://<IP-адрес-VPS>:8550` в Safari на iPhone/iPad и
выберите «На главный экран» — получите полноэкранное приложение.

## Supabase как база сервера

Заготовка: при `DB_BACKEND=supabase` сервер хранит данные в Supabase
(выполните `supabase/schema.sql`, создайте пользователей в Auth). Активный
вариант сейчас — `sqlite`.
