"""Configuration Management with Pydantic"""

from pathlib import Path
from typing import List, Optional, SecretStr

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # IRC
    irc_host: str = "irc.libera.chat"
    irc_port: int = 6667
    irc_nick: str = "PiRCBot"
    irc_user: str = "PiRC"
    irc_realname: str = "PiRC v2.0"
    irc_password: Optional[SecretStr] = None
    irc_channels: List[str] = ["#test"]

    # Security
    max_commands_per_minute: int = 10
    ban_duration_seconds: int = 3600
    max_message_length: int = 512

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8080

    # Logging
    log_level: str = "INFO"
    log_path: Path = Path("logs/pirc.log")

    # OpenTelemetry
    otel_service_name: str = "pirc"
    otel_exporter_otlp_endpoint: Optional[str] = None


settings = Settings()
