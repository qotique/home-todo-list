import json
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


def _load_config_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (ValueError, OSError):
        return {}


class Config:
    def __init__(
        self, env_path: str = ".env", config_path: str = "app_config.json"
    ) -> None:
        _load_env(env_path)
        file_cfg = _load_config_json(config_path)
        self.db_backend: str = os.getenv("DB_BACKEND", "sqlite")
        self.db_path: str = os.getenv("DB_PATH", "family_todo.db")
        self.api_url: str = (
            file_cfg.get("api_url")
            or os.getenv("API_URL")
            or "http://127.0.0.1:8000"
        )
        if not self.api_url.startswith(("http://", "https://")):
            self.api_url = "http://" + self.api_url
        self.supabase_url: str = os.getenv("SUPABASE_URL", "")
        self.supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
        self.supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.host: str = os.getenv("HOST", "0.0.0.0")


def get_config(env_path: str = ".env") -> Config:
    return Config(env_path)
