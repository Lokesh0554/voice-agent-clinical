from fastapi.testclient import TestClient

from app.main import app


def test_agent_turn_api_returns_trace_and_latency():
    client = TestClient(app)
    response = client.post(
        "/api/agent/turn",
        json={
            "session_id": "s-api",
            "patient_id": "p001",
            "audio_text": "Book an appointment with Dr Iyer tomorrow at 13",
            "channel": "inbound",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["trace"]
    assert "first_audio_ready_ms" in body["latency"]
