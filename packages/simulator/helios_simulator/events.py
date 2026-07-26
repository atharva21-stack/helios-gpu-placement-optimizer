from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class EventType(StrEnum):
    WORKLOAD_ARRIVAL = "workload_arrival"
    WORKLOAD_COMPLETION = "workload_completion"
    NODE_FAILURE = "node_failure"
    NODE_RECOVERY = "node_recovery"
    MAINTENANCE_START = "maintenance_start"
    MAINTENANCE_END = "maintenance_end"


@dataclass(order=True, frozen=True)
class Event:
    at: datetime
    type: EventType = field(compare=False)
    target_id: str = field(compare=False)
    payload: dict[str, Any] = field(default_factory=dict, compare=False)
