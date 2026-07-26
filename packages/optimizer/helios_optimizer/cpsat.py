"""Global CP-SAT placement, with a deterministic heuristic fallback."""

from __future__ import annotations

from collections.abc import Iterable
from time import perf_counter

from .candidate_generation import generate_candidates, rejection_reasons
from .domain import Allocation, Fleet, PlacementResult, Rejection, Workload
from .explanation import explain_placement
from .scoring import topology_score
from .topology_heuristic import place as heuristic_place

try:
    from ortools.sat.python import cp_model
except ImportError:  # pragma: no cover - depends on optional distribution extra
    cp_model = None


TIME_LIMITS = {"fast": 1.0, "balanced": 5.0, "thorough": 30.0}


def available() -> bool:
    return cp_model is not None


def place(
    fleet: Fleet,
    workloads: Iterable[Workload],
    *,
    mode: str = "balanced",
    fallback: bool = True,
) -> PlacementResult:
    items = tuple(workloads)
    if cp_model is None:
        if not fallback:
            raise RuntimeError("OR-Tools is not installed; install optimizer[cpsat]")
        result = heuristic_place(fleet, items)
        return PlacementResult(
            result.allocations,
            result.rejections,
            result.fleet,
            "cpsat_fallback",
            result.runtime_ms,
            result.objective_value,
        )

    started = perf_counter()
    candidates = {w.id: generate_candidates(w, fleet) for w in items}
    model = cp_model.CpModel()
    variables = {
        (w.id, index): model.NewBoolVar(f"x_{w.id}_{index}")
        for w in items
        for index in range(len(candidates[w.id]))
    }
    for w in items:
        model.Add(sum(variables[w.id, i] for i in range(len(candidates[w.id]))) <= 1)
    for node in fleet.nodes:
        terms = []
        for w in items:
            for i, candidate in enumerate(candidates[w.id]):
                demand = dict(candidate.gpus_by_node).get(node.id, 0)
                if demand:
                    terms.append(demand * variables[w.id, i])
        if terms:
            model.Add(sum(terms) <= node.free_gpus)
    objective_terms = []
    for w in items:
        for i, candidate in enumerate(candidates[w.id]):
            quality = int(round(topology_score(candidate, w)))
            value = 10000 * w.priority + 1000 * w.gpu_count + quality
            objective_terms.append(value * variables[w.id, i])
    model.Maximize(sum(objective_terms))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = TIME_LIMITS.get(mode, TIME_LIMITS["balanced"])
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return (
            heuristic_place(fleet, items)
            if fallback
            else PlacementResult(
                (),
                tuple(Rejection(w.id, ("CP-SAT found no feasible solution",)) for w in items),
                fleet,
                "cpsat",
                (perf_counter() - started) * 1000,
            )
        )

    state = fleet
    allocations: list[Allocation] = []
    rejections: list[Rejection] = []
    for w in items:
        chosen = next(
            (
                candidate
                for i, candidate in enumerate(candidates[w.id])
                if solver.BooleanValue(variables[w.id, i])
            ),
            None,
        )
        if chosen is None:
            rejections.append(Rejection(w.id, rejection_reasons(w, state)))
            continue
        allocations.append(
            Allocation(
                w.id,
                "cpsat",
                chosen.node_ids,
                cross_rack=chosen.cross_rack,
                score=topology_score(chosen, w),
                explanation=explain_placement(chosen, w, state),
                metadata={"gpus_by_node": dict(chosen.gpus_by_node)},
            )
        )
        state = state.allocate(chosen)
    return PlacementResult(
        tuple(allocations),
        tuple(rejections),
        state,
        "cpsat",
        (perf_counter() - started) * 1000,
        solver.ObjectiveValue(),
    )


cpsat = place
