"""Zentrale Konfiguration.

Alle Werte kommen aus Umgebungsvariablen. Die Defaults sind so gewaehlt,
dass der Dienst ohne jede Konfiguration lokal startet. Cloud-Umgebungen
setzen nur, was von diesen Defaults abweicht.
"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Laufzeit
    port: int = 8000
    log_level: str = "INFO"

    # Welche Korrektur-Implementierung aktiv ist.
    # "rules"  -> regelbasiert, laeuft ueberall ohne weitere Abhaengigkeit
    # "model"  -> trainiertes Modell hinter einem HTTP-Endpunkt
    corrector_backend: Literal["rules", "model"] = "rules"

    # Nur fuer corrector_backend="model" noetig.
    azure_endpoint_url: str | None = None
    azure_endpoint_key: str | None = None

    # Unterhalb dieser Konfidenz gilt eine Eingabe als "kein Befehl".
    min_confidence: float = 0.6


settings = Settings()
