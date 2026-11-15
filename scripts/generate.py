"""Generates synthetic training data for the model based corrector.

Commands are built from the vocabulary and then distorted with the
error patterns actually observed in the Whisper logs: compound words
split apart, vowels shifted by the speaker's accent, digits spoken as
words and misheard as homophones.

Training happens on this synthetic set, measuring on the real labelled
one. Mixing the two would only show that the model learned the noise
generator.
"""

import csv
import random
import re
from pathlib import Path

from app.vocabulary import ACTIONS, ENTITIES

OUT = Path("data/synthetic.csv")
SEED = 20261115
VARIANTS_PER_ALIAS = 14

# "brightness" is a valid keyword inside a sentence but nobody opens a
# command with it, so it is not used as a sentence starter here.
SKIP_ACTION_WORDS = {"brightness"}

COMPOUNDS = {
    "bedroom": "bed room",
    "bookshelf": "book shelf",
}

VOWEL_SHIFTS = [("bed", "bad"), ("bed", "back"), ("ted", "tad")]

# Spoken forms and how they were misheard. Applied to a standalone
# number, never to the letter suffix of a bulb ("1a" -> "one a").
DIGIT_WORDS = {
    "1": ["one", "won"],
    "2": ["two", "too", "to", "crew"],
    "3": ["three", "free"],
    "4": ["four", "for"],
    "5": ["five"],
    "6": ["six"],
    "7": ["seven"],
}

HOMOPHONES = {
    "living": ["let me", "team living"],
    "room": ["grow", "rome"],
    "lights": ["lines", "lice"],
    "alexandria": ["alex andrea", "alexandra"],
    "kitchen": ["kitchin", "kitten"],
    "entrance": ["entrants", "entrance is"],
}

PERCENTAGES = [10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 100]

_BULB = re.compile(r"\b(\d)([ab])\b")
_PLAIN_DIGIT = re.compile(r"\b(\d+)\b(?![ab]\b)")


def spoken_digits(text: str, rng: random.Random) -> str:
    """Replaces a number with a spoken or misheard form.

    A bulb suffix is split first, so "1a" becomes "one a" and never
    "onea".
    """
    def bulb(match: re.Match) -> str:
        digit, letter = match.group(1), match.group(2)
        return f"{rng.choice(DIGIT_WORDS.get(digit, [digit]))} {letter}"

    text = _BULB.sub(bulb, text)

    def plain(match: re.Match) -> str:
        digit = match.group(1)
        return rng.choice(DIGIT_WORDS.get(digit, [digit]))

    return _PLAIN_DIGIT.sub(plain, text, count=1)


def distort(text: str, rng: random.Random) -> str:
    """Applies one or two of the observed error patterns."""
    for _ in range(rng.choice([1, 1, 2])):
        choice = rng.random()
        if choice < 0.25:
            for whole, split in COMPOUNDS.items():
                if whole in text:
                    text = text.replace(whole, split)
                    break
        elif choice < 0.45:
            for src, dst in VOWEL_SHIFTS:
                if src in text:
                    text = text.replace(src, dst)
                    break
        elif choice < 0.70:
            text = spoken_digits(text, rng)
        else:
            for word, options in HOMOPHONES.items():
                if word in text:
                    text = text.replace(word, rng.choice(options))
                    break
    return text


def phrase(action_word: str, alias: str, action_id: str, rng: random.Random) -> str:
    """Builds one plausible sentence.

    An article is only added where the alias does not bring its own,
    and a brightness command carries a percentage, because that is how
    it is actually spoken.
    """
    article = "" if alias.startswith(("all ", "the ")) else rng.choice(["", "the "])
    sentence = f"{action_word} {article}{alias}".strip()
    if action_id == "set_brightness":
        sentence += f" to {rng.choice(PERCENTAGES)} percent"
    return sentence


def main() -> None:
    rng = random.Random(SEED)
    rows: set[tuple[str, str, str]] = set()

    for entity_id, entry in ENTITIES.items():
        for alias in entry["aliases"]:
            for action_id, action_aliases in ACTIONS.items():
                # An appliance is switched, not dimmed.
                if action_id == "set_brightness" and entry["kind"] == "appliance":
                    continue
                for action_word in action_aliases:
                    if action_word in SKIP_ACTION_WORDS:
                        continue
                    rows.add((phrase(action_word, alias, action_id, rng), action_id, entity_id))
                    for _ in range(VARIANTS_PER_ALIAS):
                        clean = phrase(action_word, alias, action_id, rng)
                        rows.add((distort(clean, rng).strip(), action_id, entity_id))

    ordered = sorted(rows)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "action", "entity"])
        writer.writerows(ordered)

    by_entity: dict[str, int] = {}
    for _, _, entity in ordered:
        by_entity[entity] = by_entity.get(entity, 0) + 1

    print(f"{len(ordered)} rows -> {OUT}")
    print(f"{len(by_entity)} classes, "
          f"min {min(by_entity.values())} / max {max(by_entity.values())} per class")


if __name__ == "__main__":
    main()
