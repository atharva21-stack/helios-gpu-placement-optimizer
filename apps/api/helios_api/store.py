from __future__ import annotations

from dataclasses import dataclass, field

from .schemas import FleetImport, PlacementRun, Workload


@dataclass
class MemoryStore:
    fleets: dict[str, FleetImport] = field(default_factory=dict)
    workloads: dict[str, Workload] = field(default_factory=dict)
    runs: dict[str, PlacementRun] = field(default_factory=dict)


store = MemoryStore()
