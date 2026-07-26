from __future__ import annotations

from collections.abc import Callable, Iterable
from time import perf_counter

from .candidate_generation import generate_candidates, rejection_reasons
from .domain import Allocation, Candidate, Fleet, PlacementResult, Rejection, Workload
from .explanation import explain_placement


def workload_sort_key(workload: Workload):
    return (
        -workload.priority,
        workload.start_time,
        -workload.gpu_count,
        -workload.constraint_count,
        -workload.duration_hours,
        workload.preemptible,
    )


def run_greedy(
    fleet: Fleet,
    workloads: Iterable[Workload],
    *,
    strategy: str,
    choose: Callable[[list[Candidate], Workload], Candidate],
) -> PlacementResult:
    started = perf_counter()
    state = fleet
    allocations: list[Allocation] = []
    rejections: list[Rejection] = []
    for workload in sorted(workloads, key=workload_sort_key):
        candidates = generate_candidates(workload, state)
        if not candidates:
            rejections.append(Rejection(workload.id, rejection_reasons(workload, state)))
            continue
        candidate = choose(candidates, workload)
        allocations.append(
            Allocation(
                workload_id=workload.id,
                strategy=strategy,
                assigned_nodes=candidate.node_ids,
                cross_rack=candidate.cross_rack,
                score=candidate.score,
                explanation=explain_placement(candidate, workload, state),
                metadata={"gpus_by_node": dict(candidate.gpus_by_node)},
            )
        )
        state = state.allocate(candidate)
    return PlacementResult(
        tuple(allocations),
        tuple(rejections),
        state,
        strategy,
        runtime_ms=(perf_counter() - started) * 1000,
    )
