"""Rule based correction: version 1, the baseline.

Works without a model and without network access, so it behaves
identically in every environment. Also serves as the yardstick the
later model based variant has to beat.
"""

import re
from difflib import SequenceMatcher

from app.config import settings
from app.corrector.base import Candidate, Correction
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
    """Brings raw transcript text into a comparable form."""
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


_INDEX = re.compile(r"\s*(\d+[ab]?)$")


def split_index(expression: str) -> tuple[str, str | None]:
    """Separates a trailing number from the rest.

    "bedroom 2" -> ("bedroom", "2"), "library 1b" -> ("library", "1b"),
    "kitchen" -> ("kitchen", None).
    """
    match = _INDEX.search(expression)
    if not match:
        return expression, None
    return expression[: match.start()].strip(), match.group(1)


def similarity(a: str, b: str) -> float:
    """Similarity of two expressions, ignoring whitespace.

    Dropping the spaces is the decisive step: speech recognition
    regularly splits compound names into two words
    ("bedroom" -> "bad room").
    """
    return SequenceMatcher(None, a.replace(" ", ""), b.replace(" ", "")).ratio()


def score(expression: str, alias: str) -> float:
    """How well an expression matches an alias.

    The wording is compared loosely, because misheard words are the
    normal case. A trailing number is compared strictly, because it
    decides which device is meant and a wrong one would switch the
    wrong lamp.
    """
    expr_base, expr_index = split_index(expression)
    alias_base, alias_index = split_index(alias)
    base = similarity(expr_base, alias_base)
    if expr_index == alias_index:
        return base
    return base * settings.index_mismatch_penalty


class RuleCorrector:
    """Corrects transcripts by matching them against the vocabulary."""

    name = "rules"

    def __init__(self) -> None:
        # Longest aliases first so that "turn off" wins over "turn on"
        # and no shorter prefix matches by accident.
        self._actions = sorted(
            all_action_aliases(), key=lambda pair: -len(pair[0])
        )
        self._entities = all_entity_aliases()

    def _rank(self, expression: str) -> list[Candidate]:
        """Best confidence per entity, highest first."""
        best: dict[str, float] = {}
        for alias, entity_id in self._entities:
            value = score(expression, alias)
            if value > best.get(entity_id, 0.0):
                best[entity_id] = value
        ranked = sorted(best.items(), key=lambda item: -item[1])
        return [Candidate(entity, round(value, 3)) for entity, value in ranked]

    def correct(self, text: str) -> Correction:
        result = Correction(raw=text)
        norm = normalize(text)
        if not norm:
            return result

        # Extract brightness before the rest is read as the target.
        match = _PERCENT.search(norm)
        if match:
            result.value = min(100, int(match.group(1)))
            norm = _PERCENT.sub(" ", norm).strip()

        # Action at the start of the sentence.
        rest = norm
        for alias, action in self._actions:
            if norm.startswith(alias):
                result.action = action
                rest = norm[len(alias):].strip()
                break

        if result.action is None:
            result.value = None
            return result

        if result.value is not None:
            result.action = "set_brightness"

        if not rest:
            return result

        ranked = self._rank(rest)
        top = ranked[0]
        result.confidence = top.confidence

        if top.confidence >= settings.min_confidence:
            result.status = "command"
            result.entity = top.entity
            result.targets = resolve(top.entity)
        elif top.confidence >= settings.clarify_confidence:
            result.status = "clarify"
            result.candidates = [
                c for c in ranked[: settings.max_candidates]
                if c.confidence >= settings.clarify_confidence
            ]

        return result
