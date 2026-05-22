from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, WebSocket

from app.models import AgentRequest, Campaign
from app.services.agent import ClinicalAgent
from app.services.repository import repo

router = APIRouter()
agent = ClinicalAgent(repo)


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/patients")
async def patients():
    return repo.list_patients()


@router.get("/doctors")
async def doctors():
    return repo.list_doctors()


@router.get("/appointments")
async def appointments(patient_id: str | None = None):
    return repo.list_appointments(patient_id)


@router.post("/agent/turn")
async def agent_turn(payload: AgentRequest):
    return await agent.handle(payload)


@router.post("/campaigns/reminders")
async def create_reminder(patient_id: str, appointment_id: str | None = None):
    campaign = Campaign(
        patient_id=patient_id,
        appointment_id=appointment_id,
        reason="appointment_reminder",
        scheduled_for=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    return repo.save_campaign(campaign)


@router.websocket("/ws/voice")
async def voice_socket(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        response = await agent.handle(AgentRequest(**data))
        await websocket.send_json(response.model_dump(mode="json"))
