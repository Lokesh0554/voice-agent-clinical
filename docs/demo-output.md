# Demo Output Checklist

Use this checklist before submitting the repository.

## Required Artifacts

- GitHub repository with source code.
- README with setup, architecture, memory, latency, tradeoffs, and limitations.
- Architecture diagram: `docs/architecture.pdf`.
- Loom walkthrough up to 3 minutes.

## Backend Commands

```powershell
cd "C:\Users\lokesh kandakurthi\Documents\Codex\2026-05-22\i-will-you-give-you-project\backend"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Swagger:

```text
http://127.0.0.1:8010/docs
```

Polished app UI:

```text
http://127.0.0.1:8010/app
```

## Expected Proof Points

- `5 passed` from backend tests.
- `POST /api/agent/turn` returns `200 OK`.
- Response includes `text`, `language`, `trace`, `latency`, and `session`.
- `trace` shows real tool calls such as `book_appointment`.
- Repeating the same doctor/time request returns unavailable slot alternatives.
- Hindi or Tamil input changes the response language and persists preference.
- Outbound rejection logs a campaign outcome.

## Honest Limitations To Mention

- No external OpenAI, Groq, STT, TTS, or telephony API is required for the local demo.
- Browser/frontend voice uses local browser speech features.
- Repository is in-memory for demo; Redis/Postgres are documented extension points.
- Deterministic local reasoning is used to keep latency low and traces easy to inspect.
