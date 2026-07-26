"""Dependency-free domain objects used by the placement engine."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from typing import Any


class Strategy(StrEnum):
    FIRST_FIT = "first_fit"
    BEST_FIT = "best_fit"
    TOPOLOGY_AWARE = "topology_aware"
    CPSAT = "cpsat"


@dataclass(frozen=True)
class Region:
    id: str
    name: str = ""
    country: str = ""
    status: str = "active"


@dataclass(frozen=True)
class Cluster:
    id: str
    region_id: str = ""
    name: str = ""
    environment: str = "production"
    network_fabric: str = ""
    storage_tier: str = ""
    supported_accelerators: tuple[str, ...] = ()
    scheduling_domain: str = ""
    status: str = "active"


@dataclass(frozen=True)
class Rack:
    id: str
    cluster_id: str
    name: str = ""
    failure_domain: str = ""
    network_domain: str = ""
    power_domain: str = ""
    status: str = "active"


@dataclass(frozen=True)
class GPUDevice:
    id: str
    node_id: str
    device_index: int
    accelerator_class: str
    hbm_total_gb: float
    uuid: str = ""
    health_status: str = "healthy"
    allocation_id: str | None = None
    reservation_id: str | None = None

    @property
    def free(self) -> bool:
        return (
            self.health_status == "healthy"
            and self.allocation_id is None
            and self.reservation_id is None
        )


@dataclass(frozen=True)
class Node:
    id: str
    cluster_id: str
    rack_id: str
    accelerator_class: str
    gpu_count: int
    hbm_per_gpu_gb: float
    hostname: str = ""
    cpu_cores: int = 0
    system_memory_gb: float = 0
    local_storage_tb: float = 0
    pcie_generation: int | None = None
    nvlink_domain: str | None = None
    nvswitch_domain: str | None = None
    infiniband_domain: str | None = None
    network_bandwidth_gbps: float = 0
    health_status: str = "healthy"
    maintenance_status: str = "available"
    maintenance_start: datetime | None = None
    maintenance_end: datetime | None = None
    tenant_scope: str | None = None
    labels: dict[str, str] = field(default_factory=dict)
    taints: tuple[str, ...] = ()
    allocated_gpus: int = 0
    reserved_gpus: int = 0
    devices: tuple[GPUDevice, ...] = ()

    @property
    def free_gpus(self) -> int:
        if self.devices:
            return sum(device.free for device in self.devices)
        return max(0, self.gpu_count - self.allocated_gpus - self.reserved_gpus)

    def with_allocated(self, count: int) -> Node:
        if count < 0 or count > self.free_gpus:
            raise ValueError(f"cannot allocate {count} GPUs on {self.id}")
        if self.devices:
            remaining = count
            devices = []
            for device in self.devices:
                if remaining and device.free:
                    devices.append(replace(device, allocation_id="helios-planned"))
                    remaining -= 1
                else:
                    devices.append(device)
            return replace(self, devices=tuple(devices))
        return replace(self, allocated_gpus=self.allocated_gpus + count)


@dataclass(frozen=True)
class Reservation:
    id: str
    cluster_id: str
    start_time: datetime
    end_time: datetime
    gpu_count: int
    accelerator_class: str
    workload_id: str | None = None
    reservation_type: str = "exclusive"
    priority: int = 0
    status: str = "active"
    node_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Workload:
    id: str
    accelerator_class: str
    gpu_count: int
    gpus_per_node: int
    node_count: int
    start_time: datetime
    end_time: datetime
    name: str = ""
    tenant_id: str = ""
    project_id: str = ""
    workload_type: str = "batch"
    priority: int = 0
    hbm_required_per_gpu_gb: float = 0
    cpu_required_per_node: int = 0
    memory_required_per_node_gb: float = 0
    storage_required_tb: float = 0
    storage_tier_required: str | None = None
    nvlink_required: bool = False
    nvswitch_required: bool = False
    infiniband_required: bool = False
    rack_local_required: bool = False
    same_failure_domain_required: bool = False
    failure_domain_spread: bool = False
    tenant_isolation: str = "shared"
    preemptible: bool = False
    migratable: bool = False
    migration_cost: float = 0
    sla_tier: str = ""
    status: str = "pending"

    def __post_init__(self) -> None:
        if min(self.gpu_count, self.gpus_per_node, self.node_count) <= 0:
            raise ValueError("GPU and node counts must be positive")
        if self.gpu_count != self.gpus_per_node * self.node_count:
            raise ValueError("gpu_count must equal gpus_per_node * node_count")
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")

    @property
    def constraint_count(self) -> int:
        return sum(
            (
                self.nvlink_required,
                self.nvswitch_required,
                self.infiniband_required,
                self.rack_local_required,
                self.same_failure_domain_required,
                self.failure_domain_spread,
                self.tenant_isolation != "shared",
            )
        )

    @property
    def duration_hours(self) -> float:
        return (self.end_time - self.start_time).total_seconds() / 3600


@dataclass(frozen=True)
class Fleet:
    nodes: tuple[Node, ...]
    clusters: tuple[Cluster, ...] = ()
    racks: tuple[Rack, ...] = ()
    reservations: tuple[Reservation, ...] = ()

    def node_map(self) -> dict[str, Node]:
        return {node.id: node for node in self.nodes}

    def allocate(self, candidate: Candidate) -> Fleet:
        demand = dict(candidate.gpus_by_node)
        return replace(
            self,
            nodes=tuple(
                node.with_allocated(demand[node.id]) if node.id in demand else node
                for node in self.nodes
            ),
        )


@dataclass(frozen=True)
class Candidate:
    workload_id: str
    node_ids: tuple[str, ...]
    gpus_by_node: tuple[tuple[str, int], ...]
    cross_rack: bool = False
    locality: float = 0
    exact_fit: bool = False
    unused_gpus: int = 0
    partial_node_delta: int = 0
    stranded_gpu_delta: int = 0
    contiguous_blocks_preserved: int = 0
    headroom: int = 0
    maintenance_risk: float = 0
    score: float = 0


@dataclass(frozen=True)
class Rejection:
    workload_id: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class Allocation:
    workload_id: str
    strategy: str
    assigned_nodes: tuple[str, ...]
    assigned_gpu_devices: tuple[str, ...] = ()
    cross_rack: bool = False
    score: float = 0
    explanation: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlacementResult:
    allocations: tuple[Allocation, ...]
    rejections: tuple[Rejection, ...]
    fleet: Fleet
    strategy: str
    runtime_ms: float = 0
    objective_value: float | None = None
