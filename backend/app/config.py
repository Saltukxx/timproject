from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional


def _get_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_float(value: Optional[str], default: float) -> float:
    try:
        return float(value) if value is not None else default
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    google_api_key: Optional[str]
    enable_ai_summary: bool
    google_model: str
    ai_timeout_seconds: float
    default_energy_limit_kwh: float


@lru_cache()
def get_settings() -> Settings:
    return Settings(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        enable_ai_summary=_get_bool(os.getenv("ENABLE_AI_SUMMARY"), default=False),
        google_model=os.getenv("GOOGLE_AI_MODEL", "models/gemini-pro"),
        ai_timeout_seconds=_get_float(os.getenv("AI_TIMEOUT_SECONDS"), default=12.0),
        default_energy_limit_kwh=_get_float(os.getenv("DEFAULT_ENERGY_LIMIT_KWH"), default=1000.0),
    )


settings = get_settings()
