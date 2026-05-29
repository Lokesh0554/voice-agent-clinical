# Real-Time Multilingual Voice AI Agent

Clinical appointment booking demo for English, Hindi, and Tamil conversations.

## Introduction

This project is a real-time multilingual voice AI agent for a digital healthcare appointment desk. The agent can manage appointment booking, rescheduling, cancellation, conflict handling, and outbound reminder follow-ups without human intervention.

The implementation focuses on systems design rather than only a visual demo. The backend exposes a traceable agent pipeline, explicit tool orchestration, appointment scheduling logic, patient/session memory, multilingual handling, and per-turn latency measurements. A polished local web app is served from FastAPI at `/app` for recording the Loom walkthrough.

## Assignment Fit

The project covers the main assignment requirements:

- Voice conversation agent: browser microphone and speech synthesis hooks, plus transcript-based demo input.
- Multilingual support: English, Hindi, and Tamil language detection with localized responses.
- Contextual memory: active session state and persistent patient preference memory.
- Outbound campaign mode: reminder campaign creation and response handling.
- Scheduling and conflict logic: prevents past-time bookings, double booking, and unavailable doctor selections.
- Tool orchestration: appointment and campaign actions go through explicit tools with visible traces.
- Latency tracking: every turn logs STT, language, reasoning, TTS, and first-audio timing.
- Documentation: README, architecture diagram, demo checklist, and Loom walkthrough guide.

## What Is Included

- Python FastAPI backend with a traceable agent loop.
- Polished backend-served app UI at `/app` for the Loom/demo.
- Optional TypeScript React frontend scaffold.
- Appointment scheduling tools that prevent double booking, past slots, and unknown doctor bookings.
- Session memory plus cross-session patient preferences.
- Per-turn latency breakdown from speech end/transcript receipt to first audio URL.
- Architecture diagram in [docs/architecture.pdf](docs/architecture.pdf) and Mermaid source in [docs/architecture.mmd](docs/architecture.mmd).
  


## Workflow Explanation

The user can interact with the agent through the app UI or Swagger API.

### Inbound Booking Flow

1. Patient selects or speaks a request, for example: `Book an appointment with Dr Iyer tomorrow at 12`.
2. The app sends the turn to `POST /api/agent/turn`.
3. The STT adapter receives the transcript. In this local demo, browser speech or typed text is used.
4. The language detector identifies English, Hindi, or Tamil and updates patient preference if needed.
5. The agent identifies the intent: book, reschedule, cancel, or unknown.
6. The agent calls a scheduling tool through `ToolRegistry`.
7. The scheduler checks doctor availability, past-time validity, and double-booking conflicts.
8. The appointment is created, rejected, cancelled, or alternatives are returned.
9. The TTS adapter prepares the response audio reference. The browser can speak the text using `speechSynthesis`.
10. The response returns agent text, trace, latency, and updated session memory.

### Conflict Flow

If the same doctor and slot are requested twice:

1. The scheduler detects an existing booked appointment.
2. The booking tool returns `ok: false`.
3. The scheduler generates nearby valid alternatives.
4. The agent responds with a graceful unavailable-slot message and alternatives.

### Outbound Reminder Flow

1. The app or API creates a reminder campaign with `POST /api/campaigns/reminders`.
2. The user switches to outbound mode.
3. If the patient declines, for example `No, not now please`, the agent calls `log_campaign_outcome`.
4. The campaign is marked declined and a polite response is returned.

## Quick Start

The polished demo app is served by the FastAPI backend, so the main assignment demo does not require a separate frontend server.

### 1. Clone And Enter The Project

```bash
git clone https://github.com/Lokesh0554/voice-agent-clinical.git
cd voice-agent-clinical/backend
```

### 2. Create A Python Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Tests

```bash
pytest
```

Expected result:

```text
5 passed
```

### 5. Start The Local App

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Open the polished app:

```text
http://127.0.0.1:8010/app
```

Swagger remains available at:

```text
http://127.0.0.1:8010/docs
```

## Demo Prompts

- English: `Book an appointment with Dr Iyer tomorrow at 12`
- Conflict: run the same prompt twice for the same doctor and slot.
- Hindi: `namaste, appointment book karna hai kal 10 baje`
- Tamil: `vanakkam, naalai appointment book seiya vendum`
- Reschedule: `Change my appointment to tomorrow evening`
- Cancel: `Cancel my appointment`
- Outbound rejection: click `Reminder`, then send `No, not now please`

## Sample Output

Input:

```text
Book an appointment with Dr Iyer tomorrow at 12
```

Typical API response:

```json
{
  "text": "Done, I booked Dr. Iyer for 23 May 12:00 PM.",
  "language": "en",
  "audio_url": "demo://tts/en/1666550451486981317",
  "trace": [
    {
      "name": "book_appointment",
      "arguments": {
        "patient_id": "p001",
        "doctor_hint": "Dr. Iyer",
        "starts_at": "2026-05-23T12:00:00+00:00"
      },
      "result": {
        "ok": true,
        "appointment": {
          "patient_id": "p001",
          "doctor_id": "d001",
          "starts_at": "2026-05-23T12:00:00Z",
          "minutes": 30,
          "status": "booked"
        },
        "alternatives": []
      },
      "elapsed_ms": 0.22
    }
  ],
  "latency": {
    "stt_ms": 0.01,
    "language_ms": 0.05,
    "reasoning_ms": 0.35,
    "tts_ms": 0.02,
    "first_audio_ready_ms": 0.48
  }
}
```

In the app UI, the same output is shown as readable cards: agent response, first-audio latency, tool count, latency breakdown, appointment details, and alternatives.

## Architecture

```mermaid
flowchart LR
  Browser["App UI<br/>Mic, TTS, barge-in"] --> API["FastAPI REST/WebSocket"]
  API --> STT["STT Adapter<br/>Browser/local demo"]
  STT --> Agent["Clinical Agent<br/>intent + tool orchestration"]
  Agent --> Memory["Session Memory<br/>active intent, pending state"]
  Agent --> Profile["Patient Memory<br/>language, history, notes"]
  Agent --> Tools["Tool Registry<br/>book, reschedule, cancel, campaign"]
  Tools --> Scheduler["Scheduling Engine<br/>conflict checks"]
  Scheduler --> Store["Repository<br/>Redis/Postgres-ready boundary"]
  Agent --> TTS["TTS Adapter<br/>first audio URL"]
  TTS --> Browser
```

The diagram artifact requested for submission lives at `docs/architecture.pdf`.

### Component Responsibilities

| Component | Responsibility |
| --- | --- |
| App UI | Presents the appointment desk, sends turns to the backend, shows response, trace, and latency. |
| FastAPI API | Exposes REST and WebSocket endpoints for voice turns, campaigns, patients, doctors, and appointments. |
| STT Adapter | Normalizes incoming speech/transcript. Demo mode uses typed/browser transcript input. |
| Language Service | Detects English, Hindi, or Tamil and persists returning-patient language preference. |
| Clinical Agent | Selects intent, coordinates memory, calls tools, and formats the patient-facing response. |
| Tool Registry | Provides explicit callable tools such as booking, rescheduling, cancellation, campaign logging, and language updates. |
| Scheduler | Validates doctor availability, rejects past slots, prevents double booking, and proposes alternatives. |
| Repository | Stores patients, doctors, appointments, sessions, and campaigns. It is in-memory for demo and replaceable with Redis/Postgres. |
| TTS Adapter | Produces a demo audio reference and lets the browser speak the response locally. |

### Request/Response Path

```text
Browser/App
  -> FastAPI /api/agent/turn
  -> STT adapter
  -> Language detection
  -> Agent intent planner
  -> ToolRegistry
  -> Scheduler + Repository
  -> TTS adapter
  -> Response with text, trace, latency, session memory
```

## Agentic Reasoning And Tool Orchestration

The agent does not return fixed canned responses directly from routes. Each turn flows through:

1. STT adapter.
2. Language detection with patient preference persistence.
3. Intent selection.
4. Tool calls through `ToolRegistry`.
5. Scheduling or campaign state mutation.
6. TTS adapter.
7. Trace and latency emission.

Every response includes a `trace` array with tool name, arguments, result, and tool elapsed time. The app pretty-prints this trace for the demo, while Swagger exposes the raw JSON.

## Memory Design

Active session memory is stored in `SessionState`:

- current language
- active intent
- pending confirmation
- turn count
- transcript

Cross-session memory is stored on the patient profile:

- language preference
- preferred doctor
- notes and prior preferences
- future extension point for appointment history and embeddings

The repository is currently in memory to keep the demo runnable. The boundary is intentionally isolated in `backend/app/services/repository.py`, so Redis with TTL can replace session storage and Postgres can replace appointment/profile storage without changing the agent or tools.

Recommended production layout:

- Redis: session state, TTL 30-60 minutes, campaign call locks.
- Postgres: patients, doctors, appointments, campaigns, audit logs.
- Vector store: summarized previous conversations retrieved by patient ID and specialty.

## Latency Budget

Target: under 450 ms from speech end to first audio response.

The demo measures from transcript receipt because browser STT performs speech capture before the backend receives the turn. Response payloads include:

- `stt_ms`
- `language_ms`
- `reasoning_ms`
- `tts_ms`
- `first_audio_ready_ms`
- `total_ms`

On a local deterministic run, these should be far below 450 ms. With production STT/TTS/LLM providers, the intended optimizations are:

- streaming STT with endpointing
- small intent/tool planning model before larger fallback model
- cached patient context
- pre-warmed TTS voices
- respond with first audio chunk before full synthesis completes
- WebSocket transport to avoid request setup overhead

## Outbound Campaign Mode

`POST /api/campaigns/reminders?patient_id=p001` creates a reminder campaign. A subsequent agent turn with `channel=outbound` and the returned `campaign_id` logs accepted or declined outcomes. The app `Reminder` button drives this path.

For production, a background queue such as Celery, Dramatiq, or BullMQ would schedule calls, enforce retries, and integrate with telephony providers.

## Tradeoffs

- STT/TTS are local adapters for demoability. The interfaces are ready for Deepgram, Azure Speech, ElevenLabs, or Twilio Media Streams.
- Language detection is lightweight and deterministic. Production should use streaming language ID plus user preference.
- Intent planning is rule-led to keep latency predictable. A production version can route ambiguous turns to an LLM planner while preserving the same tool registry.
- In-memory data is not durable. It is deliberately behind a repository boundary.

## Known Limitations

- Browser microphone support depends on Chrome-compatible Web Speech APIs.
- No real telephony provider is wired in.
- No authentication or PHI-grade security is included in this assignment demo.
- Hindi/Tamil responses are simple localized templates, not fully natural LLM generations.

## Tests

```bash
cd backend
pytest
```
