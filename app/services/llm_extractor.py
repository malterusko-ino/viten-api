"""LLM-based claim extraction service using Ollama via instructor + openai."""

import logging
import time

import instructor
import openai
from pydantic import BaseModel

from app.core.config import settings
from app.schemas.claim import ClaimbaseResponse, ExtractedClaim

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Neutral system prompt – derived strictly from docs/AI_NEUTRALITY.md
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a scientific fact-checking engine. Your sole task is to
analyse political text and extract verifiable factual claims from it.

FUNDAMENTAL RULE – NEUTRALITY:
You evaluate STATEMENTS, never persons, parties, or ideologies. You must not
express any political opinion or moral judgement. You are a neutral instrument
of science, not a political commentator.

STEP 1 – CLAIM EXTRACTION (what to extract):
Only extract claims that are objectively verifiable against official data or
scientific literature. Ignore opinions, value judgements, and pure prognoses.
- IGNORE  (opinion):   "Taxes in Germany are far too high and unjust."
- EXTRACT (fact):      "Germany has the highest tax burden of all OECD states."
If the text contains no verifiable factual claims, return an empty list.

STEP 2 – VERDICT (exactly one of four labels per claim):
Use these strict definitions – no other values are permitted:
- SUPPORTED:    Official statistics (e.g. Destatis) or broad scientific consensus
                clearly support the claim.
- REFUTED:      The claim clearly contradicts official figures or scientific
                consensus.
- MIXED:        The claim is partially true, omits important context (cherry-
                picking), or the evidence is ambivalent.
- INCONCLUSIVE: There is insufficient reliable data to objectively verify the
                claim (e.g. pure forecasts or ethical value judgements).

STEP 3 – SOURCES:
For every claim cite the most authoritative source you know of. Prioritise in
this order:
1. Official statistics: Destatis, Deutsche Bundesbank, Eurostat.
2. Parliamentary / ministerial research: Wissenschaftliche Dienste des
   Bundestages, BAMF, UBA.
3. Peer-reviewed studies and recognised economic institutes: ifo, DIW.
4. Media reports only if they directly link to a primary public document.

OUTPUT FORMAT:
Return your answer ONLY as a raw JSON object. Do NOT wrap it in markdown code
fences (no ```json ... ```). The JSON must conform to the schema you are given.
Respond in the same language as the input text."""

# ---------------------------------------------------------------------------
# Intermediate Pydantic model for instructor
# (original_text and metadata are added by the caller, not the LLM)
# ---------------------------------------------------------------------------


class LLMClaimsPayload(BaseModel):
    """The subset of ClaimbaseResponse that the LLM is responsible for."""

    extracted_claims: list[ExtractedClaim]


# ---------------------------------------------------------------------------
# instructor client (module-level, reused across requests)
# ---------------------------------------------------------------------------
_openai_client = openai.AsyncOpenAI(
    base_url=settings.ollama_base_url,
    api_key=settings.ollama_api_key,
)
_client: instructor.AsyncInstructor = instructor.from_openai(_openai_client)


# ---------------------------------------------------------------------------
# Public service function
# ---------------------------------------------------------------------------
async def extract_claims_from_text(text: str) -> ClaimbaseResponse:
    """
    Send *text* to the local Ollama LLM and return a validated ClaimbaseResponse.

    Raises:
        openai.APIConnectionError: when Ollama is unreachable (caller maps → 502).
        openai.APITimeoutError:    when the request times out (caller maps → 504).
    """
    logger.info(
        "Sending extraction request to Ollama (model=%s, text_len=%d)",
        settings.ollama_model,
        len(text),
    )
    start = time.monotonic()

    payload: LLMClaimsPayload = await _client.chat.completions.create(
        model=settings.ollama_model,
        response_model=LLMClaimsPayload,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )

    processing_time_ms = int((time.monotonic() - start) * 1000)
    logger.info("Ollama responded in %d ms", processing_time_ms)

    from app.schemas.claim import AnalysisMetadata  # local import avoids cycle

    return ClaimbaseResponse(
        original_text=text,
        extracted_claims=payload.extracted_claims,
        metadata=AnalysisMetadata(
            processing_time_ms=processing_time_ms,
            model_used=settings.ollama_model,
        ),
    )
