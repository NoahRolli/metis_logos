"""Request and response schema of the API."""

from pydantic import BaseModel, Field

from app.corrector.base import Correction


class CorrectRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Raw speech-to-text output",
    )


class CandidateOut(BaseModel):
    entity: str
    confidence: float


class CorrectResponse(BaseModel):
    raw: str
    status: str
    is_command: bool
    action: str | None
    entity: str | None
    value: int | None
    confidence: float
    targets: list[str]
    candidates: list[CandidateOut]
    backend: str

    @classmethod
    def from_correction(cls, c: Correction, backend: str) -> "CorrectResponse":
        return cls(
            raw=c.raw,
            status=c.status,
            is_command=c.is_command,
            action=c.action,
            entity=c.entity,
            value=c.value,
            confidence=c.confidence,
            targets=c.targets,
            candidates=[
                CandidateOut(entity=x.entity, confidence=x.confidence)
                for x in c.candidates
            ],
            backend=backend,
        )
