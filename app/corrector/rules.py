"""Regelbasierte Korrektur: Version 1, die Basislinie.

Arbeitet ohne Modell und ohne Netzzugriff, laeuft damit in jeder
Umgebung identisch. Dient zugleich als Vergleichsmassstab fuer die
spaetere modellbasierte Variante.
"""

import re
from difflib import SequenceMatcher

from app.config import settings
from app.corrector.base import Correction
from app.vocabulary import all_action_aliases, all_entity_aliases, resolve

NUMBER_WORDS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "won": "1", "too": "2", "ate": "8",
}

FILLER = {"the", "a", "an", "please", "of", "my", "all", "to", "for"}

_PERCENT = re.compile(r"(\d{1,3})\s*(?:percent|%)")
_BULB_SUFFIX = re.compile(r"(\d)\s+([ab])\b")


def normalize(text: str) -> str:
    """Bringt rohen Transkript-Text auf eine vergleichbare Form."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9%\s]", " ", text)
    tokens = []
    for token in text.split():
        if token in FILLER:
            continue
        tokens.append(NUMBER_WORDS.get(token, token))
    text = " ".join(tokens)
    text = _BULB_SUFFIX.sub(r"\1\2", text)   # "1 a" -> "1a"
    return re.sub(r"\s+", " ", text).strip()


def similarity(a: str, b: str) -> float:
    """Aehnlichkeit zweier Ausdruecke, ohne Leerzeichen.

    Das Entfernen der Leerzeichen ist der entscheidende Schritt: die
    Spracherkennung zerlegt zusammengesetzte Namen regelmaessig in zwei
    Woerter ("bedroom" -> "bad room").
    """
    return SequenceMatcher(None, a.replace(" ", ""), b.replace(" ", "")).ratio()


class RuleCorrector:
    """Korrigiert Transkripte durch Abgleich mit dem Vokabular."""

    name = "rules"

    def __init__(self) -> None:
        # Laengste Aliase zuerst, damit "turn off" vor "turn on" greift
        # und nicht versehentlich ein kuerzeres Praefix gewinnt.
        self._actions = sorted(
            all_action_aliases(), key=lambda pair: -len(pair[0])
        )
        self._entities = all_entity_aliases()

    def correct(self, text: str) -> Correction:
        result = Correction(raw=text)
        norm = normalize(text)
        if not norm:
            return result

        # Helligkeit herausloesen, bevor der Rest als Ziel gelesen wird.
        match = _PERCENT.search(norm)
        if match:
            result.value = min(100, int(match.group(1)))
            norm = _PERCENT.sub(" ", norm).strip()

        # Aktion am Satzanfang.
        rest = norm
        for alias, action in self._actions:
            if norm.startswith(alias):
                result.action = action
                rest = norm[len(alias):].strip()
                break

        if result.action is None:
            return result

        if result.value is not None:
            result.action = "set_brightness"

        if not rest:
            return result

        # Bestes Ziel: hoechste Aehnlichkeit, bei Gleichstand der
        # laengere und damit spezifischere Alias.
        best_alias, best_entity, best_score = max(
            (
                (alias, entity_id, similarity(rest, alias))
                for alias, entity_id in self._entities
            ),
            key=lambda item: (item[2], len(item[0])),
        )

        if best_score < settings.min_confidence:
            return result

        result.entity = best_entity
        result.confidence = round(best_score, 3)
        result.targets = resolve(best_entity)
        return result
