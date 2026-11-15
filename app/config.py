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

    # At or above this confidence the command is executed directly.
    min_confidence: float = 0.6

    # Between clarify_confidence and min_confidence the service asks
    # back instead of guessing. Below it the input counts as noise.
    clarify_confidence: float = 0.35

    # How many candidates a clarification offers.
    max_candidates: int = 3

    # A number is the part of a command that carries the most meaning:
    # "bedroom 1" and "bedroom 2" are different lamps although the words
    # are nearly identical. When the numbers disagree the match is cut
    # down by this factor, which pushes it into the clarify range
    # instead of letting it win outright.
    index_mismatch_penalty: float = 0.45


settings = Settings()
