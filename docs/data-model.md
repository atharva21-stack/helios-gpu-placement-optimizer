# Data model

Helios models physical topology separately from time-bound demand.

```text
Region 1─* Cluster 1─* Rack 1─* Node 1─* GPUDevice
                   │             │
                   └─* Reservation
Workload 1─* Allocation *─1 PlacementRun
Scenario 1─* ScenarioEvent
Scenario 1─* PlacementRun
```

## Inventory

`Region`, `Cluster`, `Rack`, `Node`, and `GPUDevice` form the physical hierarchy. Stable string identifiers are preferred because imported infrastructure systems already have canonical names. Nodes carry capacity and topology-domain labels; devices carry health and allocation state.

Topology domains such as NVLink, NVSwitch, InfiniBand, network, power, and failure domains are explicit indexed values rather than inferred from names. Capacity is never cached on parent records; it is calculated from devices and active reservations for a requested time window.

## Demand

A `Workload` is a desired shape and policy, not a running process. Its GPU class/count, per-node shape, HBM, topology, tenancy, resilience, and time window are validated together. Workload definitions may be revised; each placement run snapshots the exact input revision.

`Reservation` removes capacity for an interval. `Allocation` is the strategy's decision for one workload in one run and stores node/device assignments, score, deltas, and explanation. It does not mutate a cluster scheduler.

## Runs and scenarios

`PlacementRun` is immutable after completion. It stores input snapshot, strategy/configuration, status, aggregate metrics, runtime, and result payload. Individual allocations remain queryable for tables and exports.

`Scenario` overlays ordered events—arrival, failure, maintenance, reservation change, or capacity addition—on a baseline snapshot. Scenario execution never changes production inventory.

## Invariants

- A GPU device belongs to exactly one node.
- Node and device accelerator classes agree.
- Workload and reservation windows have `start < end`.
- One device cannot have overlapping allocations or reservations in the same run state.
- Assigned GPU counts equal the workload request.
- Completed runs are append-only; retries create a new attempt linked to the original request.
