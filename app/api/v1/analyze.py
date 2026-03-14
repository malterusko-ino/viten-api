"""Router for POST /api/v1/analyze."""

import logging

import openai
from fastapi import APIRouter, HTTPException

from app.schemas.claim import AnalyzeRequest, ClaimbaseResponse
from app.services.llm_extractor import extract_claims_from_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post("/analyze", response_model=ClaimbaseResponse, status_code=200)
async def analyze(request: AnalyzeRequest) -> ClaimbaseResponse:
    """
    Extract and scientifically evaluate verifiable claims from political text.

    Delegates to the LLM extraction service and maps service-level errors to
    appropriate HTTP status codes.
    """
    logger.info("Received analyze request (text_len=%d)", len(request.text))

    try:
        return await extract_claims_from_text(request.text)
    except openai.APIConnectionError as exc:
        logger.error("Cannot reach Ollama: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=(
                "The LLM backend (Ollama) is unreachable. "
                "Make sure Ollama is running on the configured address."
            ),
        ) from exc
    except openai.APITimeoutError as exc:
        logger.error("Ollama request timed out: %s", exc)
        raise HTTPException(
            status_code=504,
            detail="The LLM backend did not respond in time. Please try again.",
        ) from exc
    except openai.APIStatusError as exc:
        logger.error("Ollama returned an error status: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"LLM backend error: {exc.message}",
        ) from exc
