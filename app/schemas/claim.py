"""Pydantic V2 schemas for the /api/v1/analyze contract."""

import uuid
from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ScientificVerdict(str, Enum):
    """Strictly-defined verdict labels as per AI_NEUTRALITY.md."""

    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    MIXED = "MIXED"
    INCONCLUSIVE = "INCONCLUSIVE"


class Source(BaseModel):
    """A single scientific / official source supporting a verdict."""

    model_config = ConfigDict(frozen=True)

    title: str
    institution: str
    url: str | None = None
    date_published: date
    relevance_snippet: str


class ExtractedClaim(BaseModel):
    """One verifiable factual claim extracted from the original text."""

    model_config = ConfigDict(frozen=True)

    claim_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    statement: str = Field(
        description="The extracted, verifiable core claim in neutral language."
    )
    scientific_verdict: ScientificVerdict
    confidence_score: float = Field(ge=0.0, le=1.0)
    explanation: str = Field(
        description="Neutral, science-based contextualisation of the verdict."
    )
    sources: list[Source]


class AnalysisMetadata(BaseModel):
    """Processing metadata returned alongside the analysis result."""

    model_config = ConfigDict(frozen=True)

    processing_time_ms: int = Field(ge=0)
    model_used: str


class ClaimbaseResponse(BaseModel):
    """Top-level response envelope for POST /api/v1/analyze."""

    model_config = ConfigDict(frozen=True)

    original_text: str
    extracted_claims: list[ExtractedClaim]
    metadata: AnalysisMetadata


class AnalyzeRequest(BaseModel):
    """Request body for POST /api/v1/analyze."""

    text: str = Field(
        min_length=10,
        description="The political text to be analysed for verifiable claims.",
    )
