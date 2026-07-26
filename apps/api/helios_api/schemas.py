from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class APIModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class Node(APIModel):
    id: str
    cluster_id: str | None = None
    rack_id: str | None = None
    accelerator_class: str
    gpu_count: int = Field(gt=0)
    hbm_per_gpu_gb: float = Field(gt=0)
    health_status: str = "healthy"
    maintenance_status: str = "available"
    nvlink_domain: str | None = None
    nvswitch_domain: str | None = None
    infiniband_domain: str | None = None


class FleetImport(APIModel):
    regions: list[dict[str, Any]] = Field(default_factory=list)
    clusters: list[dict[str, Any]] = Field(default_factory=list)
    racks: list[dict[str, Any]] = Field(default_factory=list)
    nodes: list[Node]


class FleetSummary(BaseModel):
    fleet_id: str
    nodes: int
    total_gpus: int
    available_gpus: int
    accelerators: dict[str, int]
    racks: int
    clusters: int


class Workload(APIModel):
    id: str
    name: str | None = None
    tenant_id: str | None = None
    project_id: str | None = None
    workload_type: str = "batch"
    priority: int = 0
    accelerator_class: str
    gpu_count: int = Field(gt=0)
    gpus_per_node: int | None = Field(default=None, gt=0)
    node_count: int | None = Field(default=None, gt=0)
    hbm_required_per_gpu_gb: float = Field(default=0, ge=0)
    start_time: datetime | None = None
    end_time: datetime | None = None
    nvlink_required: bool = False
    nvswitch_required: bool = False
    infiniband_required: bool = False
    rack_local_required: bool = False

    @model_validator(mode="after")
    def validate_shape(self) -> Workload:
        if self.gpus_per_node and self.node_count:
            if self.gpus_per_node * self.node_count < self.gpu_count:
                raise ValueError("gpus_per_node * node_count must cover gpu_count")
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class WorkloadImport(APIModel):
    workloads: list[Workload]


Strategy = Literal["first_fit", "best_fit", "topology_aware", "cpsat"]


class EvaluationRequest(BaseModel):
    fleet_id: str
    workload: Workload | None = None
    workload_id: str | None = None
    strategy: Strategy = "topology_aware"

    @model_validator(mode="after")
    def workload_source(self) -> EvaluationRequest:
        if (self.workload is None) == (self.workload_id is None):
            raise ValueError("provide exactly one of workload or workload_id")
        return self


class PlacementRequest(BaseModel):
    fleet_id: str
    workload_ids: list[str] | None = None
    workloads: list[Workload] | None = None
    strategy: Strategy = "topology_aware"

    @model_validator(mode="after")
    def workload_source(self) -> PlacementRequest:
        if self.workload_ids is not None and self.workloads is not None:
            raise ValueError("provide workload_ids or workloads, not both")
        return self


class Allocation(BaseModel):
    workload_id: str
    assigned_nodes: list[str]
    assigned_gpus: dict[str, int]
    cross_rack: bool
    score: float
    explanation: list[str]


class Rejection(BaseModel):
    workload_id: str
    reasons: list[str]


class EvaluationResponse(BaseModel):
    feasible: bool
    allocation: Allocation | None = None
    reasons: list[str] = Field(default_factory=list)


class PlacementRun(BaseModel):
    id: str
    fleet_id: str
    strategy: Strategy
    status: Literal["completed"]
    started_at: datetime
    completed_at: datetime
    runtime_ms: float
    accepted_workloads: int
    rejected_workloads: int
    fleet_utilization: float
    allocations: list[Allocation]
    rejections: list[Rejection]
