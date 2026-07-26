"""Candidate objective functions."""

from __future__ import annotations

from dataclasses import replace

from .domain import Candidate, Workload


def best_fit_score(candidate: Candidate) -> float:
    return -(
        candidate.unused_gpus + 8 * max(0, candidate.partial_node_delta) + 20 * candidate.cross_rack
    )


def topology_score(candidate: Candidate, workload: Workload) -> float:
    return (
        100 * candidate.locality
        + 50 * candidate.exact_fit
        + 40 * candidate.contiguous_blocks_preserved
        + 30 * candidate.headroom
        - 50 * candidate.stranded_gpu_delta
        - 30 * candidate.partial_node_delta
        - 20 * candidate.cross_rack
        - 10 * candidate.maintenance_risk
        - 5 * workload.migration_cost
    )


def scored(candidate: Candidate, workload: Workload, mode: str) -> Candidate:
    value = best_fit_score(candidate) if mode == "best_fit" else topology_score(candidate, workload)
    return replace(candidate, score=value)
