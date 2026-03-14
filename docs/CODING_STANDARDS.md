# Viten API: Coding Standards

## 1. Tooling & Dependencies (`uv`)
- Wir nutzen `uv`.
- Um ein Paket hinzuzufügen: `uv add <package>`
- Um einen Befehl auszuführen: `uv run <command>` (z.B. `uv run fastapi dev app/main.py`)
- Erstelle keine `requirements.txt`. Die Quelle der Wahrheit ist die `pyproject.toml` und `uv.lock`.

## 2. Modernes Python (3.11+) & Type Hinting
- **Kein veraltetes Typing:** Nutze die nativen Python 3.11+ Typen. Verwende `list[str]` statt `List[str]`, `dict[str, Any]` statt `Dict` und den Pipe-Operator `|` statt `Union` (z.B. `str | None` statt `Optional[str]`).
- **Strikte Signaturen:** Jede Funktion und Methode MUSS vollständige Argument- und Return-Typen haben.
- **Pydantic V2:** Nutze ausschließlich Pydantic V2 Syntax. Verwende `model_validate()` statt `parse_obj()`, `model_dump()` statt `dict()` und `ConfigDict` statt der inneren `class Config`.

## 3. Asynchrone Programmierung (WICHTIG!)
Da dieses Backend intensiv mit LLMs und externen Datenbanken (RAG) kommuniziert, ist I/O-Performance kritisch.
- **Niemals blockieren:** Verwende NIEMALS `time.sleep()`. Nutze `await asyncio.sleep()`.
- **HTTP-Requests:** Das Paket `requests` ist strengstens verboten, da es blockierend ist. Nutze AUSSCHLIESSLICH `httpx.AsyncClient()` für externe API-Aufrufe.
- **Parallelisierung:** Wenn mehrere unabhängige Quellen abgefragt werden müssen (z.B. Destatis und Bundestag gleichzeitig), nutze `asyncio.gather()`, um sie parallel statt sequenziell auszuführen.

## 4. Konfiguration & Secrets
- **Keine Hardcodes:** API-Keys, Datenbank-URLs oder Model-Namen dürfen NIEMALS im Quellcode stehen.
- **Pydantic Settings:** Erstelle eine `Settings`-Klasse in `app/core/config.py` (basierend auf `pydantic-settings`), die alle Variablen aus der `.env`-Datei liest.
- Überall im Code wird dann nur das instanziierte `settings`-Objekt importiert.

## 5. Error Handling & Logging
- **Verbot von Print:** Die Verwendung von `print()` im produktiven Code ist untersagt. Nutze das Standard-`logging`-Modul von Python oder idealerweise `loguru`, falls es via `uv` installiert wurde.
- **Spezifische Exceptions:** Fange keine generischen Exceptions (`except Exception:`) ab, ohne sie zu loggen. Fange immer spezifische Fehler (z.B. `httpx.HTTPError`, `pydantic.ValidationError`).
- **API Responses:** Wenn in einem Service ein Fehler auftritt, wirf eine benutzerdefinierte Exception. Der FastAPI-Router fängt diese ab und wandelt sie in eine saubere `HTTPException` (inkl. passendem Status-Code wie 400, 404, 422 oder 502) um.

## 6. Dependency Injection (FastAPI)
- Nutze FastAPIs `Depends()`, um Datenbank-Sessions, Konfigurationen oder externe Clients in deine Router zu injizieren.
- Vermeide globale Zustände (Global State). Clients wie der LLM-Client oder der `httpx`-Client sollten beim Start der App (Lifespan-Events) initialisiert und bei Beendigung sauber geschlossen werden.

## 7. Linting & Formatting (Ruff)
- Der Code muss so geschrieben sein, dass er einen strikten `ruff`-Check besteht.
- Halte die Zeilenlänge im Rahmen (max. 88-100 Zeichen).
- Sortiere Imports logisch: Zuerst Standard-Bibliotheken, dann Third-Party (FastAPI, Pydantic), dann lokale Projekt-Imports.