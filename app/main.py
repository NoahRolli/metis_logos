"""HTTP-Schnittstelle.

Duenne Huelle um die Korrekturlogik. Welche Implementierung laeuft,
entscheidet ausschliesslich die Konfiguration.
"""

import logging

from fastapi import FastAPI

from app.config import settings
from app.corrector.rules import RuleCorrector
from app.models import CorrectRequest, CorrectResponse

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("metis_logos")


def build_corrector():
    if settings.corrector_backend == "rules":
        return RuleCorrector()
    raise NotImplementedError(
        f"Backend '{settings.corrector_backend}' ist noch nicht implementiert."
    )


corrector = build_corrector()

app = FastAPI(
    title="metis_logos",
    description="Korrigiert Transkripte zu gueltigen Smart-Home-Befehlen.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "backend": corrector.name}


@app.post("/correct", response_model=CorrectResponse)
def correct(request: CorrectRequest) -> CorrectResponse:
    result = corrector.correct(request.text)
    logger.info(
        "correct raw=%r entity=%s confidence=%.3f",
        result.raw, result.entity, result.confidence,
    )
    return CorrectResponse.from_correction(result, corrector.name)
