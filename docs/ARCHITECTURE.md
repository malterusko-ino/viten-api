# Viten API: Architektur & API Vertrag

## 1. Ordnerstruktur
Das Projekt folgt dem Controller/Service-Pattern zur sauberen Trennung von Web-Schicht und Geschäftslogik:
- `/app/api/`: FastAPI Router (Endpunkte, z.B. `/api/v1/analyze`).
- `/app/schemas/`: Pydantic V2 Modelle für Request/Response (DTOs).
- `/app/services/`: Kernlogik (LLM-Aufrufe, RAG-Pipeline, Text-Chunking).
- `/app/core/`: Konfiguration (Pydantic BaseSettings), Security, Abhängigkeiten.
- `/app/integrations/`: Schnittstellen zu externen Datenquellen (z.B. Destatis API, DIP Bundestag).

## 2. Der API-Vertrag (JSON Response)
Der wichtigste Endpunkt `/api/v1/analyze` nimmt einen politischen Text entgegen und MUSS folgendes standardisiertes JSON (definiert via Pydantic) zurückgeben:

```json
{
    "original_text": "string",
    "extracted_claims": [{
        "claim_id": "string (UUID)",
        "statement": "string (Die extrahierte, überprüfbare Kernbehauptung)",
        "scientific_verdict": "SUPPORTED | REFUTED | MIXED | INCONCLUSIVE",
        "confidence_score": "float (0.0 - 1.0)",
        "explanation": "string (Neutrale, wissenschaftliche Einordnung)",
        "sources": [{
          "title": "string",
          "institution": "string",
          "url": "string (optional)",
          "date_published": "YYYY-MM-DD",
          "relevance_snippet": "string"
        }]
    }],
    "metadata": {
        "processing_time_ms": "integer",
        "model_used": "string"
    }
}
