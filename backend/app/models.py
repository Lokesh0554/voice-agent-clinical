from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Language(StrEnum):
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"


class AppointmentStatus(StrEnum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class CampaignStatus(StrEnum):
    QUEUED = "queued"
    CONTACTED = "contacted"
    DECLINED = "declined"
    RESCHEDULED = "rescheduled"
    FAILED = "failed"


class Patient(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    phone: str
    language_preference: Language = Language.ENGLISH
    preferred_doctor_id: str | None = None
    notes: list[str] = Field(default_factory=list)
    last_seen_at: datetime | None = None


class Doctor(BaseModel):
    id: str
    name: str
    specialties: list[str]
    languages: list[Language]


class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    patient_id: str
    doctor_id: str
    starts_at: datetime
    minutes: int = 30
    status: AppointmentStatus = AppointmentStatus.BOOKED


class SessionState(BaseModel):
    session_id: str
    patient_id: str
    language: Language = Language.ENGLISH
    active_intent: str | None = None
    pending_confirmation: dict[str, Any] | None = None
    turn_count: int = 0
    transcript: list[dict[str, str]] = Field(default_factory=list)


class AgentRequest(BaseModel):
    session_id: str
    patient_id: str
    audio_text: str = Field(description="Demo STT transcript or browser speech transcript")
    channel: Literal["inbound", "outbound"] = "inbound"
    campaign_id: str | None = None


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    elapsed_ms: float


class AgentResponse(BaseModel):
    text: str
    language: Language
    audio_url: str | None = None
    trace: list[ToolCall]
    latency: dict[str, Any]
    session: SessionState


class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    patient_id: str
    appointment_id: str | None = None
    reason: str
    status: CampaignStatus = CampaignStatus.QUEUED
    scheduled_for: datetime
    outcome_note: str | None = None
