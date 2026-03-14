"""Router for POST /api/v1/analyze."""

import logging
import time
import uuid
from datetime import date

from fastapi import APIRouter

from app.schemas.claim import (
    AnalysisMetadata,
    AnalyzeRequest,
    ClaimbaseResponse,
    ExtractedClaim,
    ScientificVerdict,
    Source,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post("/analyze", response_model=ClaimbaseResponse, status_code=200)
async def analyze(request: AnalyzeRequest) -> ClaimbaseResponse:
    """
    Extract and scientifically evaluate verifiable claims from political text.

    Currently returns a hard-coded dummy response so the JSON contract can be
    validated end-to-end before the real RAG pipeline is wired up.
    """
    start = time.monotonic()
    logger.info("Received analyze request (text length=%d)", len(request.text))

    # --- Dummy response (replace with real service call later) ---
    dummy_source = Source(
        title="Bevölkerung und Erwerbstätigkeit – Ausländische Bevölkerung",
        institution="Statistisches Bundesamt (Destatis)",
        url="https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/"
        "Migration-Integration/_inhalt.html",
        date_published=date(2024, 3, 28),
        relevance_snippet=(
            "Laut Destatis lebten Ende 2022 rund 13,4 Millionen Ausländer in "
            "Deutschland, was einem Anteil von 16,1 % an der Gesamtbevölkerung "
            "entspricht."
        ),
    )

    dummy_claim = ExtractedClaim(
        claim_id=uuid.uuid4(),
        statement=(
            "Der Anteil der ausländischen Bevölkerung in Deutschland beträgt "
            "über 16 Prozent."
        ),
        scientific_verdict=ScientificVerdict.SUPPORTED,
        confidence_score=0.91,
        explanation=(
            "Die amtliche Statistik des Statistischen Bundesamts weist für das "
            "Jahr 2022 einen Ausländeranteil von 16,1 % aus. Die Aussage ist "
            "sachlich korrekt und durch offizielle Daten gestützt."
        ),
        sources=[dummy_source],
    )

    processing_time_ms = int((time.monotonic() - start) * 1000)

    response = ClaimbaseResponse(
        original_text=request.text,
        extracted_claims=[dummy_claim],
        metadata=AnalysisMetadata(
            processing_time_ms=processing_time_ms,
            model_used="dummy-v0",
        ),
    )

    logger.info("Analyze request completed in %d ms", processing_time_ms)
    return response
