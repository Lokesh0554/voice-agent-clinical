from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

from app.models import (
    Appointment,
    AppointmentStatus,
    Campaign,
    CampaignStatus,
    Doctor,
    Language,
    Patient,
    SessionState,
)


class MemoryRepository:
    """Repository boundary that can be swapped for Redis/Postgres in production."""

    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        self.patients: dict[str, Patient] = {
            "p001": Patient(
                id="p001",
                name="Ananya Rao",
                phone="+919000000001",
                language_preference=Language.ENGLISH,
                preferred_doctor_id="d001",
                notes=["Prefers morning slots", "Asked for reminders in English"],
            ),
            "p002": Patient(
                id="p002",
                name="Rahul Sharma",
                phone="+919000000002",
                language_preference=Language.HINDI,
                notes=["Returning patient for cardiology follow-up"],
            ),
            "p003": Patient(
                id="p003",
                name="Meena Subramanian",
                phone="+919000000003",
                language_preference=Language.TAMIL,
                notes=["Prefers Tamil conversation"],
            ),
        }
        self.doctors: dict[str, Doctor] = {
            "d001": Doctor(
                id="d001",
                name="Dr. Iyer",
                specialties=["general medicine"],
                languages=[Language.ENGLISH, Language.TAMIL],
            ),
            "d002": Doctor(
                id="d002",
                name="Dr. Sharma",
                specialties=["cardiology"],
                languages=[Language.ENGLISH, Language.HINDI],
            ),
            "d003": Doctor(
                id="d003",
                name="Dr. Khan",
                specialties=["dermatology"],
                languages=[Language.ENGLISH, Language.HINDI],
            ),
        }
        self.appointments: dict[str, Appointment] = {
            "a001": Appointment(
                id="a001",
                patient_id="p001",
                doctor_id="d001",
                starts_at=(now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0),
            )
        }
        self.sessions: dict[str, SessionState] = {}
        self.campaigns: dict[str, Campaign] = {}

    def get_patient(self, patient_id: str) -> Patient:
        return deepcopy(self.patients[patient_id])

    def save_patient(self, patient: Patient) -> None:
        self.patients[patient.id] = deepcopy(patient)

    def list_patients(self) -> list[Patient]:
        return [deepcopy(patient) for patient in self.patients.values()]

    def list_doctors(self) -> list[Doctor]:
        return [deepcopy(doctor) for doctor in self.doctors.values()]

    def get_session(self, session_id: str, patient_id: str) -> SessionState:
        if session_id not in self.sessions:
            patient = self.get_patient(patient_id)
            self.sessions[session_id] = SessionState(
                session_id=session_id,
                patient_id=patient_id,
                language=patient.language_preference,
            )
        return deepcopy(self.sessions[session_id])

    def save_session(self, session: SessionState) -> None:
        self.sessions[session.session_id] = deepcopy(session)

    def list_appointments(self, patient_id: str | None = None) -> list[Appointment]:
        appts = [
            appt
            for appt in self.appointments.values()
            if appt.status == AppointmentStatus.BOOKED and (patient_id is None or appt.patient_id == patient_id)
        ]
        return [deepcopy(appt) for appt in appts]

    def save_appointment(self, appointment: Appointment) -> Appointment:
        self.appointments[appointment.id] = deepcopy(appointment)
        return deepcopy(appointment)

    def save_campaign(self, campaign: Campaign) -> Campaign:
        self.campaigns[campaign.id] = deepcopy(campaign)
        return deepcopy(campaign)

    def update_campaign(self, campaign_id: str, status: CampaignStatus, note: str | None = None) -> None:
        campaign = self.campaigns[campaign_id]
        campaign.status = status
        campaign.outcome_note = note
        self.save_campaign(campaign)


repo = MemoryRepository()
