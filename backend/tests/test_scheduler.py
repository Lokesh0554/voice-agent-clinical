from datetime import datetime, timedelta, timezone

from app.services.repository import MemoryRepository
from app.services.scheduler import Scheduler


def test_scheduler_prevents_double_booking():
    repo = MemoryRepository()
    scheduler = Scheduler(repo)
    starts_at = datetime.now(timezone.utc) + timedelta(days=2)
    starts_at = starts_at.replace(hour=11, minute=0, second=0, microsecond=0)

    ok, first, _ = scheduler.book("p001", "d001", starts_at)
    blocked, second, alternatives = scheduler.book("p002", "d001", starts_at)

    assert ok is True
    assert first is not None
    assert blocked is False
    assert second is None
    assert alternatives


def test_scheduler_rejects_past_slot():
    repo = MemoryRepository()
    scheduler = Scheduler(repo)
    starts_at = datetime.now(timezone.utc) - timedelta(hours=1)

    ok, appointment, alternatives = scheduler.book("p001", "d001", starts_at)

    assert ok is False
    assert appointment is None
    assert alternatives
