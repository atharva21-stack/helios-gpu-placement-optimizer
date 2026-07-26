"""Bounded candidate enumeration with cheap pruning."""

from __future__ import annotations

from itertools import combinations
from time import monotonic

from .domain import Candidate, Fleet, Node, Workload
from .feasibility import check_candidate, node_violations


def _locality(nodes: tuple[Node, ...]) -> float:
    if len({n.nvswitch_domain for n in nodes}) == 1 and nodes[0].nvswitch_domain:
        return 1.0
    if len({n.rack_id for n in nodes}) == 1:
        return 0.8
    if len({n.infiniband_domain for n in nodes}) == 1 and nodes[0].infiniband_domain:
        return 0.7
    if len({n.cluster_id for n in nodes}) == 1:
        return 0.3
    return 0


def generate_candidates(
    workload: Workload,
    fleet: Fleet,
    *,
    max_candidates: int = 100,
    max_cross_rack_candidates: int = 20,
    timeout_ms: int = 500,
) -> list[Candidate]:
    deadline = monotonic() + timeout_ms / 1000
    eligible = [node for node in fleet.nodes if not node_violations(node, workload, fleet)]
    eligible.sort(
        key=lambda n: (n.free_gpus != workload.gpus_per_node, n.free_gpus, n.rack_id, n.id)
    )
    output: list[Candidate] = []
    cross_rack_count = 0
    for group in combinations(eligible, workload.node_count):
        if monotonic() > deadline:
            break
        free_before = [n.free_gpus for n in group]
        remaining = [free - workload.gpus_per_node for free in free_before]
        cross_rack = len({n.rack_id for n in group}) > 1
        if cross_rack and cross_rack_count >= max_cross_rack_candidates:
            continue
        before_partial = sum(
            0 < free < n.gpu_count for free, n in zip(free_before, group, strict=True)
        )
        after_partial = sum(
            0 < free < n.gpu_count for free, n in zip(remaining, group, strict=True)
        )
        candidate = Candidate(
            workload_id=workload.id,
            node_ids=tuple(n.id for n in group),
            gpus_by_node=tuple((n.id, workload.gpus_per_node) for n in group),
            cross_rack=cross_rack,
            locality=_locality(group),
            exact_fit=all(value == 0 for value in remaining),
            unused_gpus=sum(remaining),
            partial_node_delta=after_partial - before_partial,
            stranded_gpu_delta=sum(
                value for value in remaining if 0 < value < workload.gpus_per_node
            ),
            contiguous_blocks_preserved=sum(value // workload.gpus_per_node for value in remaining),
            headroom=sum(remaining),
        )
        if check_candidate(candidate, workload, fleet).feasible:
            output.append(candidate)
            cross_rack_count += cross_rack
        if len(output) >= max_candidates:
            break
    return output


def rejection_reasons(workload: Workload, fleet: Fleet) -> tuple[str, ...]:
    if not fleet.nodes:
        return ("fleet has no nodes",)
    violations = [node_violations(node, workload, fleet) for node in fleet.nodes]
    common = set(violations[0]).intersection(*violations[1:]) if violations else set()
    if common:
        return tuple(f"no node satisfies {reason}" for reason in sorted(common))
    return ("no feasible node group satisfies topology and capacity constraints",)
