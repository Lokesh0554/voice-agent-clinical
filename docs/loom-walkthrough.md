# Loom Walkthrough Script

Target length: 2.5 to 3 minutes.

## 0:00-0:25 Overview

Show the README and say:

This is a real-time multilingual clinical voice agent for appointment booking. It supports English, Hindi, and Tamil, handles booking, rescheduling, cancellation, conflict resolution, patient memory, outbound reminder campaigns, reasoning traces, and latency logging.

## 0:25-1:15 Live Demo

Open the polished app at `http://127.0.0.1:8010/app`.

Use the `Book` quick action or type:

`Book an appointment with Dr Iyer tomorrow at 12`

Click `Send turn`.

Point out:

- natural agent response
- appointment desk UI
- latency metric
- trace panel

Then open Swagger at `http://127.0.0.1:8010/docs` only if you want to show the raw API response.

Use `POST /api/agent/turn` with:

```json
{
  "session_id": "demo-session",
  "patient_id": "p001",
  "audio_text": "Book an appointment with Dr Iyer tomorrow at 12",
  "channel": "inbound",
  "campaign_id": null
}
```

Point out:

- response text
- selected language
- `trace[0].name = book_appointment`
- appointment ID and booked slot
- latency fields

Run the same request again to show conflict handling and alternatives.

## 1:15-1:45 Multilingual And Memory

Use:

```json
{
  "session_id": "demo-hindi",
  "patient_id": "p001",
  "audio_text": "नमस्ते, appointment book karna hai kal 10 baje",
  "channel": "inbound",
  "campaign_id": null
}
```

Point out:

- language switches to Hindi
- patient language preference is persisted through the update language tool
- session transcript is returned

## 1:45-2:15 Outbound Mode

Create a reminder with:

`POST /api/campaigns/reminders?patient_id=p001`

Then use the returned campaign ID in:

```json
{
  "session_id": "demo-outbound",
  "patient_id": "p001",
  "audio_text": "No, not now please",
  "channel": "outbound",
  "campaign_id": "PASTE_CAMPAIGN_ID"
}
```

Point out the `log_campaign_outcome` tool call and polite rejection.

## 2:15-3:00 Architecture

Open `docs/architecture.pdf` or README architecture section.

Explain:

- STT and TTS are adapters, currently local/demo for runnable submission.
- Agent uses a tool registry for booking, rescheduling, cancellation, campaign outcomes, and language persistence.
- Session memory tracks active conversation state.
- Patient memory stores cross-session preferences.
- Scheduling engine prevents invalid appointments.
- Redis/Postgres can replace the repository boundary in production.
- Latency is measured per stage against a 450 ms first-audio target.
