import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str
    api_prefix: str
    secret_key: str
    access_token_expire_minutes: int
    otp_expire_minutes: int
    rate_limit_requests: int
    rate_limit_window_seconds: int
    data_dir: Path


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@lru_cache
def get_settings() -> Settings:
    _load_env_file()
    data_dir = Path(__file__).resolve().parents[2] / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return Settings(
        app_name=os.getenv("APP_NAME", "Telecom MNP API"),
        api_prefix=os.getenv("API_PREFIX", "/api"),
        secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")),
        otp_expire_minutes=int(os.getenv("OTP_EXPIRE_MINUTES", "10")),
        rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "30")),
        rate_limit_window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")),
        data_dir=data_dir,
    )
