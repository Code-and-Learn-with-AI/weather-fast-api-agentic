import pytest
from pydantic import ValidationError

from app.core.config import Settings


def make_env(**overrides: str) -> dict[str, str]:
    """Return a complete valid env dict, with optional field overrides."""
    base = {
        "OPENWEATHER_API_KEY": "test-key",
        "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/weather",
        "REDIS_URL": "redis://localhost:6379/0",
    }
    return {**base, **overrides}


def test_settings_loads_with_all_required_vars() -> None:
    settings = Settings.model_validate(make_env())
    assert settings.OPENWEATHER_API_KEY == "test-key"
    assert settings.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost:5432/weather"
    assert settings.REDIS_URL == "redis://localhost:6379/0"


def test_log_level_defaults_to_info() -> None:
    settings = Settings.model_validate(make_env())
    assert settings.LOG_LEVEL == "INFO"


def test_missing_openweather_api_key_raises() -> None:
    env = make_env()
    del env["OPENWEATHER_API_KEY"]
    with pytest.raises(ValidationError):
        Settings.model_validate(env)


def test_missing_database_url_raises() -> None:
    env = make_env()
    del env["DATABASE_URL"]
    with pytest.raises(ValidationError):
        Settings.model_validate(env)


def test_missing_redis_url_raises() -> None:
    env = make_env()
    del env["REDIS_URL"]
    with pytest.raises(ValidationError):
        Settings.model_validate(env)


@pytest.mark.parametrize("level", ["DEBUG", "WARNING", "ERROR", "CRITICAL"])
def test_log_level_accepts_valid_values(level: str) -> None:
    settings = Settings.model_validate(make_env(LOG_LEVEL=level))
    assert settings.LOG_LEVEL == level


def test_log_level_rejects_invalid_value() -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate(make_env(LOG_LEVEL="VERBOSE"))
