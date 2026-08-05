# Family Todo List

Семейный todo-лист на Flet: задачи разделены на **личные** и **семейные**.
Платформы: Web (VPS), нативное Android-приложение, iOS (PWA).

## Возможности
- Логин с паролем
- Вкладки «Семейные» / «Личные»
- Приоритеты, дедлайны, назначение ответственного
- Фильтры (Все / Активные / Завершённые)
- Хранилище: SQLite или Supabase (интерфейс `Storage`)

## Структура проекта
- `app.py` — точка входа приложения
- `models.py` — модели `User`, `Task`
- `storage.py` — абстрактный интерфейс хранилища
- `storage_sqlite.py` — реализация на SQLite
- `storage_supabase.py` — реализация на Supabase
- `auth.py` — хэширование паролей (pbkdf2)
- `seed_users.py` — CLI добавления пользователей
- `ui/` — Flet-контролы (вход, навигация, список задач, диалог задачи)
- `supabase/schema.sql` — схема и RLS для Supabase
- `deploy/flet.service` — юнит systemd для VPS
- `.github/workflows/build.yml` — сборка Android APK

## Запуск локально (SQLite)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed_users.py mama Мама --password mypass
python seed_users.py papa Папа --password mypass
python app.py
```

После этого откройте `http://localhost:8000` или десктопное окно и войдите одним из созданных пользователей.

## Запуск как web-сервер на VPS

1. Скопируйте код в `/opt/home-todo-list`, создайте venv и установите зависимости:

```bash
sudo mkdir -p /opt/home-todo-list
sudo git clone git@github.com:qotique/home-todo-list.git /opt/home-todo-list
cd /opt/home-todo-list
sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt
```

2. Создайте `.env` (указывайте `STORAGE_BACKEND=sqlite` или `supabase`).

3. Создайте пользователей: `seed_users.py` (см. выше, выполнять от владельца БД).

4. Установите службу:

```bash
sudo cp deploy/flet.service /etc/systemd/system/flet.service
sudo systemctl daemon-reload
sudo systemctl enable --now flet
```

Сервис слушает порт `8000`. Убедитесь, что он открыт в фаерволе и доступен по белому IP:
`http://<IP-адрес-VPS>:8000`. Логи службы: `journalctl -u flet -f`.

## Android

Сборка APK выполняется в GitHub Actions (`.github/workflows/build.yml`) на ветке `main`.
Перейдите в раздел **Actions** → «Build Android APK» → **Run workflow**, затем скачайте артефакт
`home-todo-list-apk` (файл `flet-apk.zip`, внутри APK/AAB).

Нативное приложение использует Supabase в облаке: в `.env` указаны `SUPABASE_URL` и
`SUPABASE_ANON_KEY` (RLS). Перед сборкой запишите их в CI-секреты GitHub
(Settings → Secrets) или внесите значения в `.env` в момент сборки.

## iOS (PWA)

Native IPA не собирается (нет Apple Developer аккаунта). Вместо этого откройте web-версию
`http://<IP-адрес-VPS>:8000` в Safari на iPhone/iPad и выберите «На главный экран» —
получите полноэкранное приложение.

## Supabase

1. Создайте проект в Supabase.
2. В SQL Editor выполните содержимое `supabase/schema.sql`.
3. В Authentication → Users создайте пользователей с e-mail и паролем.
4. В `.env` пропишите:
   - `STORAGE_BACKEND=supabase`
   - `SUPABASE_URL=https://<ref>.supabase.co`
   - `SUPABASE_SERVICE_KEY=<service_role>>` (для web/VPS)
   - `SUPABASE_ANON_KEY=<anon>>` (для нативного приложения)

Web-версия на VPS при `STORAGE_BACKEND=supabase` входит через Supabase Auth (email+пароль),
RLS пропускается сервисным ключом. Нативное Android-приложение использует anon-ключ + RLS
(`supabase/schema.sql`): пользователь видит свои и семейные задачи.