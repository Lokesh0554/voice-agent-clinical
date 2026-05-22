from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.core.latency import LatencyTracker
from app.models import AgentRequest, AgentResponse, CampaignStatus, Language, SessionState
from app.services.language import detect_language, localize
from app.services.repository import MemoryRepository
from app.services.scheduler import Scheduler
from app.services.tools import ToolRegistry
from app.services.voice import SpeechToText, TextToSpeech


class ClinicalAgent:
    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        self.scheduler = Scheduler(repository)
        self.tools = ToolRegistry(repository, self.scheduler)
        self.stt = SpeechToText()
        self.tts = TextToSpeech()

    async def handle(self, payload: AgentRequest) -> AgentResponse:
        latency = LatencyTracker(str(uuid4()))
        trace = []
        session = self.repository.get_session(payload.session_id, payload.patient_id)

        with latency.span("stt_ms"):
            transcript = await self.stt.transcribe(payload.audio_text)

        with latency.span("language_ms"):
            language = detect_language(transcript, session.language)
            if language != session.language:
                trace.append(self.tools.call("update_patient_language", patient_id=payload.patient_id, language=language.value))
            session.language = language

        with latency.span("reasoning_ms"):
            text = self._reason(payload, session, transcript, trace)

        with latency.span("tts_ms"):
            audio_url = await self.tts.synthesize(text, session.language)

        session.turn_count += 1
        session.transcript.extend(
            [
                {"role": "patient", "content": transcript},
                {"role": "agent", "content": text},
            ]
        )
        self.repository.save_session(session)
        latency.mark("first_audio_ready_ms")

        return AgentResponse(
            text=text,
            language=session.language,
            audio_url=audio_url,
            trace=trace,
            latency=latency.report(),
            session=session,
        )

    def _reason(self, payload: AgentRequest, session: SessionState, transcript: str, trace: list) -> str:
        lowered = transcript.lower()
        patient = self.repository.get_patient(payload.patient_id)
        session.active_intent = self._intent(lowered)

        if payload.channel == "outbound" and payload.campaign_id and self._is_rejection(lowered):
            trace.append(
                self.tools.call(
                    "log_campaign_outcome",
                    campaign_id=payload.campaign_id,
                    status=CampaignStatus.DECLINED.value,
                    note=f"Patient declined: {transcript}",
                )
            )
            return localize("declined", session.language)

        if session.active_intent == "cancel":
            trace.append(self.tools.call("cancel_appointment", patient_id=payload.patient_id))
            return localize("cancelled", session.language)

        if session.active_intent in {"book", "reschedule"}:
            doctor_hint = self._doctor_hint(lowered, patient.preferred_doctor_id)
            starts_at = self.scheduler.parse_slot(transcript)
            tool = "reschedule_appointment" if session.active_intent == "reschedule" else "book_appointment"
            call = self.tools.call(
                tool,
                patient_id=payload.patient_id,
                doctor_hint=doctor_hint,
                starts_at=starts_at.isoformat(),
            )
            trace.append(call)
            if call.result.get("ok"):
                appointment = call.result["appointment"]
                doctor = self.repository.doctors[appointment["doctor_id"]]
                return localize(
                    "booked",
                    session.language,
                    doctor=doctor.name,
                    time=self._friendly_time(datetime.fromisoformat(appointment["starts_at"])),
                )
            if call.result.get("reason") == "doctor_not_found":
                trace.append(self.tools.call("list_doctors"))
                return localize("ask_slot", session.language)
            options = ", ".join(self._friendly_time(datetime.fromisoformat(slot)) for slot in call.result.get("alternatives", []))
            return localize("alternatives", session.language, options=options or "the next working day")

        if self._looks_like_confirmation(lowered) and session.pending_confirmation:
            pending = session.pending_confirmation
            call = self.tools.call(
                "book_appointment",
                patient_id=payload.patient_id,
                doctor_hint=pending.get("doctor_hint"),
                starts_at=pending["starts_at"],
            )
            trace.append(call)
            session.pending_confirmation = None
            if call.result.get("ok"):
                appointment = call.result["appointment"]
                doctor = self.repository.doctors[appointment["doctor_id"]]
                return localize("booked", session.language, doctor=doctor.name, time=self._friendly_time(datetime.fromisoformat(appointment["starts_at"])))

        return localize("ask_slot", session.language)

    def _intent(self, lowered: str) -> str:
        if any(token in lowered for token in ("cancel", "रद्द", "radd", "ரத்து")):
            return "cancel"
        if any(token in lowered for token in ("reschedule", "change", "shift", "बदल", "மாற்ற")):
            return "reschedule"
        if any(token in lowered for token in ("book", "appointment", "slot", "अपॉइंटमेंट", "புக்", "சந்திப்பு")):
            return "book"
        return "unknown"

    def _doctor_hint(self, lowered: str, preferred_doctor_id: str | None) -> str | None:
        for doctor in self.repository.list_doctors():
            if doctor.name.lower().replace("dr. ", "") in lowered or doctor.name.lower() in lowered:
                return doctor.name
        if "cardio" in lowered or "heart" in lowered:
            return "cardiology"
        if "skin" in lowered:
            return "dermatology"
        if preferred_doctor_id:
            return self.repository.doctors[preferred_doctor_id].name
        return None

    def _is_rejection(self, lowered: str) -> bool:
        return any(token in lowered for token in ("no", "not now", "later", "नहीं", "வேண்டாம்"))

    def _looks_like_confirmation(self, lowered: str) -> bool:
        return lowered.strip() in {"yes", "confirm", "ok", "haan", "हाँ", "seri", "சரி"}

    def _friendly_time(self, value: datetime) -> str:
        return value.strftime("%d %b %I:%M %p")
