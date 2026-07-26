from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from .placement import evaluate
from .schemas import (
    EvaluationRequest,
    EvaluationResponse,
    FleetImport,
    FleetSummary,
    PlacementRequest,
    PlacementRun,
    Rejection,
    WorkloadImport,
)
from .store import store

router = APIRouter(prefix="/api/v1")


def _fleet(fleet_id: str) -> FleetImport:
    try:
        return store.fleets[fleet_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="fleet not found") from None


def _workload(workload_id: str):
    try:
        return store.workloads[workload_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="workload not found") from None


@router.post("/fleets/{fleet_id}/import", response_model=FleetSummary, status_code=201)
def import_fleet(fleet_id: str, payload: FleetImport) -> FleetSummary:
    if len({node.id for node in payload.nodes}) != len(payload.nodes):
        raise HTTPException(status_code=409, detail="node ids must be unique")
    store.fleets[fleet_id] = payload
    return fleet_summary(fleet_id)


@router.get("/fleets/{fleet_id}/summary", response_model=FleetSummary)
def fleet_summary(fleet_id: str) -> FleetSummary:
    fleet = _fleet(fleet_id)
    accelerators: dict[str, int] = {}
    available = 0
    for node in fleet.nodes:
        accelerators[node.accelerator_class] = (
            accelerators.get(node.accelerator_class, 0) + node.gpu_count
        )
        if node.health_status.lower() == "healthy" and node.maintenance_status.lower() in {
            "available",
            "none",
        }:
            available += node.gpu_count
    return FleetSummary(
        fleet_id=fleet_id,
        nodes=len(fleet.nodes),
        total_gpus=sum(n.gpu_count for n in fleet.nodes),
        available_gpus=available,
        accelerators=accelerators,
        racks=len({n.rack_id for n in fleet.nodes if n.rack_id}),
        clusters=len({n.cluster_id for n in fleet.nodes if n.cluster_id}),
    )


@router.post("/workloads/import", status_code=201)
def import_workloads(payload: WorkloadImport) -> dict[str, int]:
    ids = [workload.id for workload in payload.workloads]
    if len(set(ids)) != len(ids):
        raise HTTPException(status_code=409, detail="workload ids must be unique")
    store.workloads.update({workload.id: workload for workload in payload.workloads})
    return {"imported": len(payload.workloads)}


@router.post("/placement/evaluate", response_model=EvaluationResponse)
def evaluate_placement(payload: EvaluationRequest) -> EvaluationResponse:
    fleet = _fleet(payload.fleet_id)
    workload = payload.workload or _workload(payload.workload_id or "")
    return evaluate(workload, fleet.nodes, strategy=payload.strategy)


@router.post("/placement/run", response_model=PlacementRun, status_code=201)
def run_placement(payload: PlacementRequest) -> PlacementRun:
    fleet = _fleet(payload.fleet_id)
    workloads = payload.workloads
    if workloads is None:
        workloads = (
            [_workload(item) for item in payload.workload_ids]
            if payload.workload_ids is not None
            else list(store.workloads.values())
        )
    workloads = sorted(
        workloads,
        key=lambda w: (
            -w.priority,
            w.start_time.timestamp() if w.start_time else float("-inf"),
            -w.gpu_count,
        ),
    )
    started = datetime.now(UTC)
    timer = perf_counter()
    allocations, rejections, used = [], [], {}
    for workload in workloads:
        result = evaluate(workload, fleet.nodes, used, payload.strategy)
        if result.allocation:
            allocations.append(result.allocation)
            for node_id, count in result.allocation.assigned_gpus.items():
                used[node_id] = used.get(node_id, 0) + count
        else:
            rejections.append(Rejection(workload_id=workload.id, reasons=result.reasons))
    total_gpus = sum(node.gpu_count for node in fleet.nodes)
    run = PlacementRun(
        id=str(uuid4()),
        fleet_id=payload.fleet_id,
        strategy=payload.strategy,
        status="completed",
        started_at=started,
        completed_at=datetime.now(UTC),
        runtime_ms=(perf_counter() - timer) * 1000,
        accepted_workloads=len(allocations),
        rejected_workloads=len(rejections),
        fleet_utilization=sum(used.values()) / total_gpus if total_gpus else 0,
        allocations=allocations,
        rejections=rejections,
    )
    store.runs[run.id] = run
    return run


@router.get("/placement/runs", response_model=list[PlacementRun])
def list_runs() -> list[PlacementRun]:
    return list(store.runs.values())


@router.get("/placement/runs/{run_id}", response_model=PlacementRun)
def get_run(run_id: str) -> PlacementRun:
    try:
        return store.runs[run_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="placement run not found"
        ) from None


@router.get("/placement/runs/{run_id}/allocations")
def get_allocations(run_id: str):
    return get_run(run_id).allocations


@router.get("/placement/runs/{run_id}/rejections")
def get_rejections(run_id: str):
    return get_run(run_id).rejections
