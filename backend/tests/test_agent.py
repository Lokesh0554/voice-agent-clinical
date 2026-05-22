import pytest

from app.models import AgentRequest, Language
from app.services.agent import ClinicalAgent
from app.services.repository import MemoryRepository


@pytest.mark.asyncio
async def test_agent_books_with_trace_and_latency():
    repo = MemoryRepository()
    agent = ClinicalAgent(repo)

    response = await agent.handle(
        AgentRequest(
            session_id="s-test",
            patient_id="p001",
            audio_text="Book an appointment with Dr Iyer tomorrow at 12",
        )
    )

    assert response.language == Language.ENGLISH
    assert response.trace[0].name == "book_appointment"
    assert response.latency["first_audio_ready_ms"] < 450


@pytest.mark.asyncio
async def test_agent_persists_language_preference():
    repo = MemoryRepository()
    agent = ClinicalAgent(repo)

    await agent.handle(
        AgentRequest(
            session_id="s-lang",
            patient_id="p001",
            audio_text="नमस्ते, appointment book karna hai kal",
        )
    )

    assert repo.get_patient("p001").language_preference == Language.HINDI
