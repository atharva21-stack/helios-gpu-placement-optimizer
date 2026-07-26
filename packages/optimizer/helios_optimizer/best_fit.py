from __future__ import annotations

from collections.abc import Iterable

from ._strategy import run_greedy
from .domain import Fleet, PlacementResult, Workload
from .scoring import scored


def place(fleet: Fleet, workloads: Iterable[Workload]) -> PlacementResult:
    return run_greedy(
        fleet,
        workloads,
        strategy="best_fit",
        choose=lambda candidates, workload: max(
            (scored(candidate, workload, "best_fit") for candidate in candidates),
            key=lambda candidate: (candidate.score, tuple(reversed(candidate.node_ids))),
        ),
    )


best_fit = place
