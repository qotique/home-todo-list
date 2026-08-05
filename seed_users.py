import argparse

from auth import hash_password
from config import get_config
from storage_sqlite import SQLiteStorage

USER_FIELDS = {
    "mother": "Мама",
    "father": "Папа",
    "son": "Сын",
    "daughter": "Дочь",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Добавить пользователя семьи")
    parser.add_argument("login", help="логин (english)")
    parser.add_argument("name", help="отображаемое имя")
    parser.add_argument("--password", help="пароль (иначе будет запрошен)")
    parser.add_argument(
        "--db", default=None, help="путь к SQLite-БД (по умолчанию из .env)"
    )
    args = parser.parse_args()

    config = get_config()
    storage = SQLiteStorage(args.db or config.db_path)

    password = args.password
    if password is None:
        import getpass

        password = getpass.getpass("Пароль: ")

    existing = storage.get_user_by_login(args.login)
    if existing:
        print(f"Пользователь '{args.login}' уже существует.")
        return

    user = storage.create_user(
        login=args.login, name=args.name, password_hash=hash_password(password)
    )
    print(f"Создан пользователь: id={user.id}, login={user.login}, name={user.name}")


if __name__ == "__main__":
    main()