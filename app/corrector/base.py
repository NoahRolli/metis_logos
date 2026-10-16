"""Gemeinsame Schnittstelle aller Korrektur-Implementierungen.

Jede Implementierung bekommt rohen Text aus der Spracherkennung und
gibt dasselbe Ergebnisobjekt zurueck. Dadurch sind die regelbasierte
und die modellbasierte Variante gegeneinander austauschbar und
vergleichbar.
"""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class Correction:
    """Das Ergebnis einer Korrektur."""

    raw: str                      # Eingabe, unveraendert
    action: str | None = None     # turn_on | turn_off | set_brightness
    entity: str | None = None     # kanonische Entitaets-ID
    value: int | None = None      # Helligkeit in Prozent, falls genannt
    confidence: float = 0.0       # 0.0 bis 1.0
    targets: list[str] = field(default_factory=list)  # aufgeloeste Geraete

    @property
    def is_command(self) -> bool:
        return self.action is not None and self.entity is not None


class Corrector(Protocol):
    """Was jede Implementierung koennen muss."""

    name: str

    def correct(self, text: str) -> Correction: ...
