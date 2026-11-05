"""Ein- und Ausgabeformat der API."""

from pydantic import BaseModel, Field

from app.corrector.base import Correction


class CorrectRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Roher Text aus der Spracherkennung",
    )


class CorrectResponse(BaseModel):
    raw: str
    is_command: bool
    action: str | None
    entity: str | None
    value: int | None
    confidence: float
    targets: list[str]
    backend: str

    @classmethod
    def from_correction(cls, c: Correction, backend: str) -> "CorrectResponse":
        return cls(
            raw=c.raw,
            is_command=c.is_command,
            action=c.action,
            entity=c.entity,
            value=c.value,
            confidence=c.confidence,
            targets=c.targets,
            backend=backend,
        )
