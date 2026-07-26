from __future__ import annotations

from collections import defaultdict
from math import ceil

from .schemas import Allocation, EvaluationResponse, Node, Strategy, Workload


def evaluate(
    workload: Workload,
    nodes: list[Node],
    used: dict[str, int] | None = None,
    strategy: Strategy = "topology_aware",
) -> EvaluationResponse:
    used = used or {}
    required_per_node = workload.gpus_per_node or workload.gpu_count
    required_nodes = workload.node_count or ceil(workload.gpu_count / required_per_node)
    reasons: list[str] = []
    matching = [n for n in nodes if n.accelerator_class == workload.accelerator_class]
    if not matching:
        reasons.append(f"no nodes provide accelerator {workload.accelerator_class}")
    healthy = [
        n
        for n in matching
        if n.health_status.lower() == "healthy"
        and n.maintenance_status.lower() in {"available", "none"}
    ]
    if matching and not healthy:
        reasons.append("matching nodes are unhealthy or in maintenance")
    eligible = [
        n
        for n in healthy
        if n.hbm_per_gpu_gb >= workload.hbm_required_per_gpu_gb
        and n.gpu_count - used.get(n.id, 0) >= required_per_node
        and (not workload.nvlink_required or n.nvlink_domain)
        and (not workload.nvswitch_required or n.nvswitch_domain)
        and (not workload.infiniband_required or n.infiniband_domain)
    ]
    if healthy and not eligible:
        reasons.append("no nodes satisfy HBM, topology, and free-GPU constraints")

    def domain(node: Node) -> str:
        if workload.rack_local_required:
            return node.rack_id or ""
        if workload.infiniband_required:
            return node.infiniband_domain or ""
        return "*"

    groups: dict[str, list[Node]] = defaultdict(list)
    for node in eligible:
        groups[domain(node)].append(node)
    candidates = [group for group in groups.values() if len(group) >= required_nodes]
    if not candidates:
        if eligible:
            reasons.append(f"no topology domain contains {required_nodes} eligible nodes")
        return EvaluationResponse(feasible=False, reasons=reasons or ["insufficient capacity"])
    pool = max(candidates, key=len)
    if strategy == "best_fit":
        pool.sort(key=lambda n: n.gpu_count - used.get(n.id, 0))
    elif strategy == "topology_aware":
        pool.sort(key=lambda n: (n.rack_id or "", n.id))
    else:
        pool.sort(key=lambda n: n.id)
    selected = pool[:required_nodes]
    remaining = workload.gpu_count
    assigned: dict[str, int] = {}
    for node in selected:
        count = min(required_per_node, remaining)
        assigned[node.id] = count
        remaining -= count
    racks = {n.rack_id for n in selected}
    allocation = Allocation(
        workload_id=workload.id,
        assigned_nodes=[n.id for n in selected],
        assigned_gpus=assigned,
        cross_rack=len(racks) > 1,
        score=float(sum(n.gpu_count - used.get(n.id, 0) - assigned[n.id] for n in selected)),
        explanation=[
            f"placed {workload.gpu_count} {workload.accelerator_class} GPUs",
            f"selected {len(selected)} node(s) using {strategy}",
        ],
    )
    return EvaluationResponse(feasible=True, allocation=allocation)
