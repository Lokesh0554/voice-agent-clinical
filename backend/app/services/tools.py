from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Callable

from app.models import CampaignStatus, Language, ToolCall
from app.services.repository import MemoryRepository
from app.services.scheduler import Scheduler


class ToolRegistry:
    def __init__(self, repository: MemoryRepository, scheduler: Scheduler) -> None:
        self.repository = repository
        self.scheduler = scheduler
        self._tools: dict[str, Callable[..., dict[str, Any]]] = {
            "list_doctors": self.list_doctors,
            "book_appointment": self.book_appointment,
            "reschedule_appointment": self.reschedule_appointment,
            "cancel_appointment": self.cancel_appointment,
            "update_patient_language": self.update_patient_language,
            "log_campaign_outcome": self.log_campaign_outcome,
        }

    def call(self, name: str, **kwargs: Any) -> ToolCall:
        start = time.perf_counter()
        result = self._tools[name](**kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        return ToolCall(name=name, arguments=kwargs, result=result, elapsed_ms=round(elapsed, 2))

    def list_doctors(self) -> dict[str, Any]:
        return {"doctors": [doctor.model_dump(mode="json") for doctor in self.repository.list_doctors()]}

    def book_appointment(self, patient_id: str, doctor_hint: str | None, starts_at: str) -> dict[str, Any]:
        doctor_id = self.scheduler.find_doctor(doctor_hint)
        if doctor_id is None:
            return {"ok": False, "reason": "doctor_not_found"}
        ok, appointment, alternatives = self.scheduler.book(patient_id, doctor_id, datetime.fromisoformat(starts_at))
        return {
            "ok": ok,
            "appointment": appointment.model_dump(mode="json") if appointment else None,
            "alternatives": [slot.isoformat() for slot in alternatives],
        }

    def reschedule_appointment(self, patient_id: str, doctor_hint: str | None, starts_at: str) -> dict[str, Any]:
        doctor_id = self.scheduler.find_doctor(doctor_hint)
        if doctor_id is None:
            return {"ok": False, "reason": "doctor_not_found"}
        ok, appointment, alternatives = self.scheduler.reschedule_latest(patient_id, doctor_id, datetime.fromisoformat(starts_at))
        return {
            "ok": ok,
            "appointment": appointment.model_dump(mode="json") if appointment else None,
            "alternatives": [slot.isoformat() for slot in alternatives],
        }

    def cancel_appointment(self, patient_id: str) -> dict[str, Any]:
        appointment = self.scheduler.cancel_latest(patient_id)
        return {"ok": appointment is not None, "appointment": appointment.model_dump(mode="json") if appointment else None}

    def update_patient_language(self, patient_id: str, language: str) -> dict[str, Any]:
        patient = self.repository.get_patient(patient_id)
        patient.language_preference = Language(language)
        self.repository.save_patient(patient)
        return {"ok": True, "language": language}

    def log_campaign_outcome(self, campaign_id: str, status: str, note: str) -> dict[str, Any]:
        self.repository.update_campaign(campaign_id, CampaignStatus(status), note)
        return {"ok": True}
