import os


def _load_env(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class Config:
    def __init__(self, env_path: str = ".env") -> None:
        _load_env(env_path)
        self.storage_backend: str = os.getenv("STORAGE_BACKEND", "sqlite")
        self.db_path: str = os.getenv("DB_PATH", "family_todo.db")
        self.api_url: str = os.getenv("API_URL", "http://127.0.0.1:8000")
        self.supabase_url: str = os.getenv("SUPABASE_URL", "")
        self.supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
        self.supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.host: str = os.getenv("HOST", "0.0.0.0")


def get_config(env_path: str = ".env") -> Config:
    return Config(env_path)
