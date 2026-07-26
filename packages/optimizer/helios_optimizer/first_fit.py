from __future__ import annotations

from collections.abc import Iterable

from ._strategy import run_greedy
from .domain import Fleet, PlacementResult, Workload


def place(fleet: Fleet, workloads: Iterable[Workload]) -> PlacementResult:
    return run_greedy(
        fleet, workloads, strategy="first_fit", choose=lambda candidates, _: candidates[0]
    )


first_fit = place
