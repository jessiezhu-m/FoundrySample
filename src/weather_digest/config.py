from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    foundry_endpoint: str
    foundry_deployment: str
    foundry_api_version: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    acs_connection_string: str
    email_from: str
    email_to: str
    schedule_timezone: str
    schedule_hour: int
    schedule_minute: int


def load_config() -> AppConfig:
    load_dotenv()

    return AppConfig(
        foundry_endpoint=_required("FOUNDRY_ENDPOINT"),
        foundry_deployment=_first_required("FOUNDRY_DEPLOYMENT", "FOUNDRY_MODEL"),
        foundry_api_version=os.getenv("FOUNDRY_API_VERSION", "2024-06-01"),
        smtp_host=os.getenv("SMTP_HOST", ""),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        acs_connection_string=_required("ACS_CONNECTION_STRING"),
        email_from=_required("EMAIL_FROM"),
        email_to=os.getenv("EMAIL_TO", "alias@microsoft.com"),
        schedule_timezone=os.getenv("SCHEDULE_TIMEZONE", "Asia/Shanghai"),
        schedule_hour=int(os.getenv("SCHEDULE_HOUR", "6")),
        schedule_minute=int(os.getenv("SCHEDULE_MINUTE", "0")),
    )


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _first_required(*names: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    raise RuntimeError(
        "Missing required environment variable: " + " or ".join(names)
    )
