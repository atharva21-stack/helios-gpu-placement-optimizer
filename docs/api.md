# HTTP API

The API is versioned under `/api/v1`. JSON uses UTC ISO-8601 timestamps and snake-case field names. Collection endpoints use cursor pagination.

## Fleet

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/fleet/summary` | Capacity, utilization, health, and fragmentation |
| `GET` | `/clusters` | List clusters with aggregate capacity |
| `POST` | `/clusters` | Create or import a cluster |
| `GET` | `/clusters/{cluster_id}/nodes` | List nodes and topology |
| `PATCH` | `/nodes/{node_id}` | Update health, maintenance, or labels |

## Workloads and reservations

| Method | Path | Purpose |
|---|---|---|
| `GET` / `POST` | `/workloads` | List or create workloads |
| `GET` / `PATCH` | `/workloads/{workload_id}` | Read or revise a workload |
| `POST` | `/workloads/{workload_id}/feasibility` | Explain current feasibility |
| `GET` / `POST` | `/reservations` | List or create reservations |

## Placement and simulation

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/placement-runs` | Start a strategy run |
| `GET` | `/placement-runs/{run_id}` | Status, metrics, and result |
| `GET` | `/placement-runs/{run_id}/allocations` | Paginated decisions |
| `GET` | `/placement-runs/{run_id}/exports/{format}` | JSON, CSV, Kubernetes, or Slurm |
| `GET` / `POST` | `/scenarios` | List or define scenarios |
| `POST` | `/scenarios/{scenario_id}/runs` | Replay a scenario |
| `POST` | `/benchmarks` | Run a repeatable strategy comparison |

## Create a placement run

```http
POST /api/v1/placement-runs
Idempotency-Key: 7ca3d286-fec4-47d9-8307-c5849f37a960
Content-Type: application/json

{
  "strategy": "topology_aware",
  "workload_ids": ["llama70b-prod", "vision-tuning"],
  "fleet_snapshot_id": "snap_20260726_1830",
  "configuration": {
    "max_candidates_per_workload": 100,
    "timeout_ms": 1000
  }
}
```

A synchronous run returns `201 Created`; a queued run returns `202 Accepted` with the same resource shape:

```json
{
  "id": "run_8f21",
  "status": "running",
  "strategy": "topology_aware",
  "progress": 0.35,
  "created_at": "2026-07-26T18:31:02Z",
  "links": {
    "self": "/api/v1/placement-runs/run_8f21",
    "allocations": "/api/v1/placement-runs/run_8f21/allocations"
  }
}
```

## Errors

Errors follow RFC 9457 problem details with `type`, `title`, `status`, `detail`, `instance`, and an optional `errors` array for field violations. Expected status codes include `409` for stale snapshots or conflicting reservations, `422` for invalid workload shapes, and `429` for exhausted run concurrency.
