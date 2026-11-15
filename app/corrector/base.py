"""Shared interface for all correction implementations.

Every implementation receives raw speech-to-text output and returns the
same result object. This keeps the rule based and the model based
variant interchangeable and directly comparable.
"""

from dataclasses import dataclass, field
from typing import Literal, Protocol

Status = Literal["command", "clarify", "no_command"]


@dataclass
class Candidate:
    """One possible target, with the confidence it was matched at."""

    entity: str
    confidence: float


@dataclass
class Correction:
    """The result of a correction."""

    raw: str                      # input, unchanged
    status: Status = "no_command"
    action: str | None = None     # turn_on | turn_off | set_brightness
    entity: str | None = None     # canonical entity id, set when status is command
    value: int | None = None      # brightness in percent, if given
    confidence: float = 0.0       # 0.0 to 1.0
    targets: list[str] = field(default_factory=list)   # resolved devices
    candidates: list[Candidate] = field(default_factory=list)  # for clarify

    @property
    def is_command(self) -> bool:
        return self.status == "command"


class Corrector(Protocol):
    """What every implementation has to provide."""

    name: str

    def correct(self, text: str) -> Correction: ...
