from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class LatencyTracker:
    request_id: str
    started_at: float = field(default_factory=time.perf_counter)
    marks: dict[str, float] = field(default_factory=dict)

    def mark(self, name: str) -> None:
        self.marks[name] = (time.perf_counter() - self.started_at) * 1000

    @contextmanager
    def span(self, name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            self.marks[name] = (time.perf_counter() - start) * 1000

    def total_ms(self) -> float:
        return (time.perf_counter() - self.started_at) * 1000

    def report(self) -> dict[str, float | str]:
        return {
            "request_id": self.request_id,
            "total_ms": round(self.total_ms(), 2),
            **{key: round(value, 2) for key, value in self.marks.items()},
        }
