"""Central configuration.

All values come from environment variables. The defaults are chosen so
that the service starts locally without any configuration at all. Cloud
environments only set what differs from these defaults.
"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Runtime
    port: int = 8000
    log_level: str = "INFO"

    # Which correction implementation is active.
    # "rules" -> rule based, runs anywhere without further dependencies
    # "model" -> trained model behind an HTTP endpoint
    corrector_backend: Literal["rules", "model"] = "rules"

    # Only needed for corrector_backend="model".
    azure_endpoint_url: str | None = None
    azure_endpoint_key: str | None = None

    # Below this confidence an input counts as "no command".
    min_confidence: float = 0.6


settings = Settings()
