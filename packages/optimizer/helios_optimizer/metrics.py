"""Fleet capacity and placement metrics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass

from .domain import Fleet, PlacementResult


@dataclass(frozen=True)
class CapacityMetrics:
    healthy_gpus: int
    allocated_gpus: int
    raw_free_gpus: int
    fully_free_nodes: int
    partial_nodes: int
    fragmented_gpus: int
    contiguous_8_gpu_nodes: int
    contiguous_16_gpu_groups: int
    contiguous_32_gpu_groups: int
    utilization: float

    def to_dict(self) -> dict:
        return asdict(self)


def calculate(fleet: Fleet, shape_gpus_per_node: int = 8) -> CapacityMetrics:
    healthy = [node for node in fleet.nodes if node.health_status == "healthy"]
    healthy_gpus = sum(node.gpu_count for node in healthy)
    allocated = sum(node.allocated_gpus for node in healthy)
    free = sum(node.free_gpus for node in healthy)
    fully_free = sum(node.free_gpus == node.gpu_count for node in healthy)
    partial = sum(0 < node.free_gpus < node.gpu_count for node in healthy)
    fragmented = sum(node.free_gpus for node in healthy if 0 < node.free_gpus < shape_gpus_per_node)
    domains: dict[str, int] = defaultdict(int)
    racks: dict[str, int] = defaultdict(int)
    for node in healthy:
        if node.free_gpus >= shape_gpus_per_node:
            domains[node.infiniband_domain or f"node:{node.id}"] += 1
            racks[node.rack_id] += 1
    return CapacityMetrics(
        healthy_gpus,
        allocated,
        free,
        fully_free,
        partial,
        fragmented,
        sum(node.free_gpus >= 8 for node in healthy),
        sum(count // 2 for count in domains.values()),
        sum(count // 4 for count in racks.values()),
        allocated / healthy_gpus if healthy_gpus else 0,
    )


def result_metrics(result: PlacementResult) -> dict:
    values = calculate(result.fleet).to_dict()
    values.update(
        {
            "accepted_workloads": len(result.allocations),
            "rejected_workloads": len(result.rejections),
            "cross_rack_placements": sum(a.cross_rack for a in result.allocations),
            "runtime_ms": result.runtime_ms,
        }
    )
    return values
