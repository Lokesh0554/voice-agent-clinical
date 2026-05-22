from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models import Appointment, AppointmentStatus
from app.services.repository import MemoryRepository


class Scheduler:
    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository

    def find_doctor(self, name_or_specialty: str | None) -> str | None:
        doctors = self.repository.list_doctors()
        if not name_or_specialty:
            return doctors[0].id
        needle = name_or_specialty.lower()
        for doctor in doctors:
            if needle in doctor.name.lower() or any(needle in specialty for specialty in doctor.specialties):
                return doctor.id
        return None

    def parse_slot(self, text: str) -> datetime:
        now = datetime.now(timezone.utc)
        lowered = text.lower()
        day_offset = 1 if any(token in lowered for token in ("tomorrow", "kal", "naalai", "நாளை")) else 0
        if any(token in lowered for token in ("day after", "parson")):
            day_offset = 2
        hour = 10
        if "evening" in lowered or "शाम" in text:
            hour = 17
        if "afternoon" in lowered or "दोपहर" in text:
            hour = 14
        for candidate in range(8, 20):
            if f"{candidate}" in lowered:
                hour = candidate if candidate >= 8 else candidate + 12
        return (now + timedelta(days=day_offset)).replace(hour=hour, minute=0, second=0, microsecond=0)

    def available_alternatives(self, doctor_id: str, desired: datetime, count: int = 3) -> list[datetime]:
        options: list[datetime] = []
        cursor = max(desired, datetime.now(timezone.utc) + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        for _ in range(48):
            if 8 <= cursor.hour <= 18 and self.is_available(doctor_id, cursor):
                options.append(cursor)
                if len(options) == count:
                    return options
            cursor += timedelta(hours=1)
        return options

    def is_available(self, doctor_id: str, starts_at: datetime) -> bool:
        if starts_at <= datetime.now(timezone.utc):
            return False
        return not any(
            appt.doctor_id == doctor_id and appt.starts_at == starts_at
            for appt in self.repository.list_appointments()
        )

    def book(self, patient_id: str, doctor_id: str, starts_at: datetime) -> tuple[bool, Appointment | None, list[datetime]]:
        if not self.is_available(doctor_id, starts_at):
            return False, None, self.available_alternatives(doctor_id, starts_at)
        return True, self.repository.save_appointment(
            Appointment(patient_id=patient_id, doctor_id=doctor_id, starts_at=starts_at)
        ), []

    def cancel_latest(self, patient_id: str) -> Appointment | None:
        appointments = sorted(self.repository.list_appointments(patient_id), key=lambda item: item.starts_at)
        if not appointments:
            return None
        appointment = appointments[0]
        appointment.status = AppointmentStatus.CANCELLED
        self.repository.save_appointment(appointment)
        return appointment

    def reschedule_latest(self, patient_id: str, doctor_id: str, starts_at: datetime) -> tuple[bool, Appointment | None, list[datetime]]:
        latest = self.cancel_latest(patient_id)
        if latest is None:
            return self.book(patient_id, doctor_id, starts_at)
        ok, appointment, alternatives = self.book(patient_id, doctor_id, starts_at)
        if not ok:
            latest.status = AppointmentStatus.BOOKED
            self.repository.save_appointment(latest)
        return ok, appointment, alternatives
