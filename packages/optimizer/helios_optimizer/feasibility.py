"""Hard-constraint validation."""

from __future__ import annotations

from dataclasses import dataclass

from .domain import Candidate, Fleet, Node, Workload


@dataclass(frozen=True)
class FeasibilityResult:
    feasible: bool
    blocking_constraints: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def overlaps(start_a, end_a, start_b, end_b) -> bool:
    return start_a < end_b and start_b < end_a


def node_violations(node: Node, workload: Workload, fleet: Fleet) -> tuple[str, ...]:
    reasons: list[str] = []
    if node.accelerator_class != workload.accelerator_class:
        reasons.append("accelerator_class")
    if node.health_status != "healthy":
        reasons.append("node_health")
    if node.maintenance_status not in ("available", "none"):
        reasons.append("maintenance_status")
    if (
        node.maintenance_start
        and node.maintenance_end
        and overlaps(
            workload.start_time, workload.end_time, node.maintenance_start, node.maintenance_end
        )
    ):
        reasons.append("maintenance_window")
    if node.hbm_per_gpu_gb < workload.hbm_required_per_gpu_gb:
        reasons.append("hbm_per_gpu")
    if node.free_gpus < workload.gpus_per_node:
        reasons.append("free_gpus")
    if node.cpu_cores < workload.cpu_required_per_node:
        reasons.append("cpu")
    if node.system_memory_gb < workload.memory_required_per_node_gb:
        reasons.append("memory")
    if node.local_storage_tb < workload.storage_required_tb:
        reasons.append("storage")
    if workload.nvlink_required and not node.nvlink_domain:
        reasons.append("nvlink")
    if workload.nvswitch_required and not node.nvswitch_domain:
        reasons.append("nvswitch")
    if workload.infiniband_required and not node.infiniband_domain:
        reasons.append("infiniband")
    if node.tenant_scope and node.tenant_scope != workload.tenant_id:
        reasons.append("tenant_scope")
    cluster = next((c for c in fleet.clusters if c.id == node.cluster_id), None)
    if workload.storage_tier_required and (
        cluster is None or cluster.storage_tier != workload.storage_tier_required
    ):
        reasons.append("storage_tier")
    for reservation in fleet.reservations:
        if reservation.status != "active" or reservation.workload_id == workload.id:
            continue
        if reservation.cluster_id != node.cluster_id:
            continue
        if reservation.node_ids and node.id not in reservation.node_ids:
            continue
        if reservation.accelerator_class != workload.accelerator_class:
            continue
        if overlaps(
            workload.start_time, workload.end_time, reservation.start_time, reservation.end_time
        ):
            reasons.append("reservation")
            break
    return tuple(dict.fromkeys(reasons))


def check_candidate(candidate: Candidate, workload: Workload, fleet: Fleet) -> FeasibilityResult:
    nodes_by_id = fleet.node_map()
    nodes = [nodes_by_id[nid] for nid in candidate.node_ids if nid in nodes_by_id]
    reasons: list[str] = []
    if len(nodes) != workload.node_count:
        reasons.append("node_count")
    if sum(dict(candidate.gpus_by_node).values()) != workload.gpu_count:
        reasons.append("gpu_count")
    for node in nodes:
        reasons.extend(node_violations(node, workload, fleet))
    if len({n.cluster_id for n in nodes}) > 1:
        reasons.append("same_cluster")
    if workload.rack_local_required and len({n.rack_id for n in nodes}) > 1:
        reasons.append("rack_local")
    if workload.nvswitch_required and len({n.nvswitch_domain for n in nodes}) > 1:
        reasons.append("same_nvswitch")
    if workload.infiniband_required and len({n.infiniband_domain for n in nodes}) > 1:
        reasons.append("same_infiniband")
    rack_map = {rack.id: rack for rack in fleet.racks}
    fds = {rack_map[n.rack_id].failure_domain for n in nodes if n.rack_id in rack_map}
    if workload.same_failure_domain_required and len(fds) > 1:
        reasons.append("same_failure_domain")
    if workload.failure_domain_spread and len(nodes) > 1 and len(fds) < len(nodes):
        reasons.append("failure_domain_spread")
    return FeasibilityResult(not reasons, tuple(dict.fromkeys(reasons)))
