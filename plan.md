# Helios — Topology-Aware GPU Placement Optimizer

> A production-style planning and simulation system that maps AI workload requirements onto a heterogeneous GPU fleet while minimizing fragmentation and preserving future allocatable capacity.

## 1. Purpose

Helios answers one question:

> Given a fleet of GPU nodes and a set of AI workloads, where should each workload be placed?

The system accepts workload requirements such as GPU type, GPU count, HBM, GPUs per node, topology, duration, priority, tenancy, maintenance, reservation, and resilience constraints. It returns feasible placements, rejected workloads, placement explanations, fragmentation metrics, remaining contiguous capacity, and comparisons across scheduling strategies.

Helios is a recommendation and simulation engine. It does not replace Kubernetes or Slurm, provision hardware, collect live telemetry, or estimate how many GPUs a model needs. A separate capacity-planning tool produces workload requirements; Helios decides where those requirements should be placed.

## 2. Core Capabilities

- Model regions, clusters, racks, nodes, GPU devices, topology domains, reservations, maintenance windows, and existing allocations.
- Accept training, fine-tuning, inference, embeddings, batch, and experimentation workloads.
- Validate accelerator, HBM, node shape, topology, tenancy, reservation, maintenance, and failure-domain constraints.
- Compare First Fit, Best Fit, Topology-Aware Heuristic, and OR-Tools CP-SAT placement.
- Measure utilization, fragmented GPUs, stranded GPUs, fully free nodes, contiguous blocks, cross-rack placements, and scheduling latency.
- Run what-if scenarios for workload arrivals, node failures, rack maintenance, reservation changes, and fleet expansion.
- Export JSON, CSV, Kubernetes affinity recommendations, and Slurm constraints.


## 3. Technology Stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Table
- React Hook Form
- Zod
- Recharts
- React Flow for topology visualization

### Backend
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- RQ or Celery

### Optimization and Simulation
- Python
- OR-Tools CP-SAT
- NetworkX
- NumPy
- Pandas
- SimPy

### Quality and Delivery
- Pytest
- Hypothesis
- Ruff
- mypy
- Playwright
- Vitest
- Docker Compose
- GitHub Actions


## 4. Repository Structure

```text
helios-gpu-placement-optimizer/
├── README.md
├── IMPLEMENTATION.md
├── LICENSE
├── Makefile
├── docker-compose.yml
├── .env.example
├── .github/workflows/
│   ├── backend-ci.yml
│   ├── frontend-ci.yml
│   └── benchmark.yml
├── apps/
│   ├── api/
│   │   ├── helios_api/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── api/
│   │   │   │   ├── routes_fleet.py
│   │   │   │   ├── routes_workloads.py
│   │   │   │   ├── routes_placement.py
│   │   │   │   ├── routes_scenarios.py
│   │   │   │   └── routes_benchmarks.py
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   └── workers/
│   │   ├── alembic/
│   │   └── tests/
│   └── web/
│       ├── app/
│       │   ├── page.tsx
│       │   ├── fleet/
│       │   ├── workloads/
│       │   ├── placement/
│       │   ├── scenarios/
│       │   └── benchmarks/
│       ├── components/
│       ├── lib/
│       └── tests/
├── packages/
│   ├── optimizer/
│   │   ├── helios_optimizer/
│   │   │   ├── domain.py
│   │   │   ├── candidate_generation.py
│   │   │   ├── feasibility.py
│   │   │   ├── scoring.py
│   │   │   ├── first_fit.py
│   │   │   ├── best_fit.py
│   │   │   ├── topology_heuristic.py
│   │   │   ├── cpsat.py
│   │   │   ├── metrics.py
│   │   │   ├── explanation.py
│   │   │   └── exports.py
│   │   └── tests/
│   ├── simulator/
│   │   ├── helios_simulator/
│   │   │   ├── events.py
│   │   │   ├── fleet_state.py
│   │   │   ├── workload_generator.py
│   │   │   ├── runner.py
│   │   │   └── reporting.py
│   │   └── tests/
│   └── synthetic_data/
│       ├── generate_fleet.py
│       ├── generate_workloads.py
│       └── fixtures/
├── scripts/
│   ├── seed_demo.py
│   ├── run_benchmarks.py
│   ├── export_report.py
│   ├── export_kubernetes.py
│   └── export_slurm.py
├── examples/
│   ├── fleet-small.yaml
│   ├── fleet-enterprise.yaml
│   ├── workloads-demo.yaml
│   └── scenarios/
└── docs/
    ├── architecture.md
    ├── optimizer.md
    ├── data-model.md
    ├── api.md
    └── benchmark-methodology.md
```


## 5. Domain Model

### Region
```text
id, name, country, status
```

### Cluster
```text
id, name, region_id, environment, network_fabric, storage_tier,
supported_accelerators, scheduling_domain, status
```

### Rack
```text
id, cluster_id, name, failure_domain, network_domain, power_domain, status
```

### Node
```text
id
cluster_id
rack_id
hostname
accelerator_class
gpu_count
hbm_per_gpu_gb
cpu_cores
system_memory_gb
local_storage_tb
pcie_generation
nvlink_domain
nvswitch_domain
infiniband_domain
network_bandwidth_gbps
health_status
maintenance_status
maintenance_start
maintenance_end
tenant_scope
labels
taints
```

### GPU Device
```text
id, node_id, device_index, uuid, accelerator_class, hbm_total_gb,
health_status, allocation_id, reservation_id
```

### Workload
```text
id
name
tenant_id
project_id
workload_type
priority
accelerator_class
gpu_count
gpus_per_node
node_count
hbm_required_per_gpu_gb
cpu_required_per_node
memory_required_per_node_gb
storage_required_tb
start_time
end_time
nvlink_required
nvswitch_required
infiniband_required
rack_local_required
same_failure_domain_required
failure_domain_spread
tenant_isolation
preemptible
migratable
migration_cost
sla_tier
status
```

### Reservation
```text
id, workload_id, cluster_id, start_time, end_time, gpu_count,
accelerator_class, reservation_type, priority, status
```

### Allocation
```text
id, workload_id, cluster_id, strategy, assigned_nodes,
assigned_gpu_devices, start_time, end_time, cross_rack,
fragmentation_delta, stranded_gpu_delta, contiguous_blocks_delta,
score, explanation
```

### Placement Run
```text
id, strategy, scenario_id, status, started_at, completed_at,
runtime_ms, accepted_workloads, rejected_workloads, fleet_utilization,
stranded_gpus, fragmented_gpus, contiguous_blocks,
cross_rack_placements, objective_value, result_payload
```


## 6. Input Files

### Example Fleet YAML

```yaml
regions:
  - id: us-central
    name: US Central

clusters:
  - id: h100-prod-01
    name: H100 Production 01
    region_id: us-central
    network_fabric: infiniband
    storage_tier: nvme
    status: active

racks:
  - id: rack-a
    cluster_id: h100-prod-01
    failure_domain: fd-a
    network_domain: ib-a
    power_domain: power-a

nodes:
  - id: h100-a-01
    cluster_id: h100-prod-01
    rack_id: rack-a
    accelerator_class: H100_80GB
    gpu_count: 8
    hbm_per_gpu_gb: 80
    cpu_cores: 192
    system_memory_gb: 2048
    local_storage_tb: 15
    nvlink_domain: nvlink-a-01
    nvswitch_domain: nvswitch-a-01
    infiniband_domain: ib-a
    network_bandwidth_gbps: 400
    health_status: healthy
    maintenance_status: available
```

### Example Workload YAML

```yaml
workloads:
  - id: llama70b-prod
    name: Llama 70B Production
    tenant_id: tenant-finance
    project_id: agent-platform
    workload_type: inference
    priority: 90
    accelerator_class: H100_80GB
    gpu_count: 16
    gpus_per_node: 8
    node_count: 2
    hbm_required_per_gpu_gb: 72
    start_time: 2026-08-01T00:00:00Z
    end_time: 2026-09-01T00:00:00Z
    nvlink_required: true
    infiniband_required: true
    tenant_isolation: dedicated
    preemptible: false
    migratable: false
    sla_tier: platinum
```


## 7. Candidate Placement Generation

The optimizer first creates valid candidate node groups.

### Steps

1. Filter nodes by accelerator class.
2. Remove unhealthy nodes.
3. Remove nodes whose maintenance windows overlap the workload.
4. Remove nodes with conflicting reservations.
5. Validate HBM per GPU.
6. Validate free GPUs per node.
7. Group nodes by NVSwitch, rack, and InfiniBand domain.
8. Generate combinations matching the requested node count.
9. Validate tenant-isolation and failure-domain policies.
10. Calculate fragmentation and contiguous-capacity impact.
11. Retain the best candidates for scoring or global optimization.

### Candidate pruning

```text
max_candidates_per_workload = 100
max_cross_rack_candidates = 20
candidate_generation_timeout_ms = 500
```

Pruning rules:

- prefer exact-fit nodes,
- prefer one topology domain,
- remove dominated candidates,
- skip cross-rack candidates unless necessary,
- cache topology and capacity calculations.


## 8. Feasibility Engine

### Hard Constraints

A candidate is rejected when any of these fail:

- Accelerator class matches.
- HBM per GPU meets the requirement.
- Total free GPU count is sufficient.
- Each selected node provides the required GPUs per node.
- Selected node count matches.
- NVLink or NVSwitch is available when required.
- InfiniBand domain is available when required.
- Maintenance does not overlap.
- Reservations do not conflict.
- Tenant-isolation rules are respected.
- Failure-domain requirements are respected.
- Required storage tier exists.
- Nodes are healthy.

### Soft Constraints

Soft constraints influence candidate rank:

- same-rack placement,
- exact fit,
- fewer partial nodes,
- more contiguous capacity preserved,
- lower cross-rack cost,
- lower migration cost,
- higher remaining headroom,
- lower maintenance risk.

### Feasibility Response

```json
{
  "feasible": true,
  "recommended_cluster": "h100-prod-01",
  "recommended_nodes": ["h100-a-01", "h100-a-02"],
  "blocking_constraints": [],
  "warnings": [
    "Placement leaves one remaining two-node H100 block"
  ],
  "capacity_impact": {
    "stranded_gpu_delta": 0,
    "fragmented_gpu_delta": 0,
    "contiguous_8_gpu_blocks_delta": -2
  },
  "explanation": [
    "Accelerator and HBM requirements are satisfied",
    "Both nodes share one InfiniBand domain",
    "No reservation or maintenance conflicts exist"
  ]
}
```


## 9. Capacity Metrics

### Raw Free GPUs

```text
raw_free_gpus = healthy_gpus - allocated_gpus - reserved_gpus
```

### Fully Free Nodes

```text
fully_free_nodes = count(nodes where free_gpus == node.gpu_count)
```

### Partial Nodes

```text
partial_nodes = count(nodes where 0 < free_gpus < node.gpu_count)
```

### Fragmented GPUs

Fragmentation is workload-shape dependent.

For a workload requiring eight GPUs on one node:

```text
fragmented_gpus =
sum(free_gpus on nodes where free_gpus < 8)
```

### Contiguous Blocks

Report:

- fully free eight-GPU nodes,
- two-node 16-GPU groups inside one InfiniBand domain,
- four-node 32-GPU groups inside one rack or fabric domain.

### Stranded GPUs

Free GPUs that cannot be used because of:

- topology,
- tenant restrictions,
- HBM mismatch,
- reservations,
- maintenance,
- node-shape incompatibility,
- or failure-domain constraints.

### Placement Utilization

```text
placement_utilization = allocated_gpus / healthy_gpus
```

### Effective Future Capacity

Replay representative future workload shapes against the resulting fleet state and count how many remain placeable.


## 10. Placement Strategies

### First Fit

1. Sort workloads by priority and start time.
2. Generate candidates.
3. Select the first feasible candidate.
4. Update fleet state.

Use this as the baseline.

### Best Fit

Select the feasible candidate that leaves the least unused node capacity.

```text
score =
unused_gpu_capacity
+ partial_node_penalty
+ cross_rack_penalty
```

### Topology-Aware Heuristic

Recommended score:

```text
score =
    100 * topology_locality
  + 50  * exact_fit
  + 40  * contiguous_blocks_preserved
  + 30  * post_placement_headroom
  - 50  * stranded_gpu_delta
  - 30  * partial_node_delta
  - 20  * cross_rack
  - 10  * maintenance_risk
  - 5   * migration_cost
```

Suggested locality values:

```text
same NVSwitch domain: 1.0
same rack:            0.8
same InfiniBand domain: 0.7
cross rack:           0.3
cross fabric domain:  0.0
```

This should be the default interactive strategy because it is fast and explainable.

### CP-SAT Optimizer

For workload `w` and candidate placement `p`:

```text
x[w,p] ∈ {0,1}
```

Each workload is placed at most once:

```text
sum_p x[w,p] <= 1
```

Node capacity:

```text
sum_(w,p containing n)
gpu_demand_on_node[w,p,n] * x[w,p]
<= available_gpus[n]
```

Suggested objective:

```text
maximize:
    10000 * accepted_priority
  + 1000  * accepted_gpu_count
  + 100   * contiguous_blocks_preserved
  + 50    * exact_fit_assignments
  - 500   * stranded_gpus
  - 200   * partial_nodes
  - 100   * cross_rack_assignments
  - 50    * workload_moves
  - 20    * risk_penalties
```

Runtime modes:

```text
Fast:      1 second
Balanced:  5 seconds
Thorough: 30 seconds
```

Return the best feasible solution when the time limit is reached.


## 11. Workload Ordering

Recommended heuristic order:

1. Highest priority
2. Earliest start time
3. Largest GPU count
4. Strictest topology requirements
5. Longest duration
6. Non-preemptible before preemptible

Example:

```python
sort_key = (
    -workload.priority,
    workload.start_time,
    -workload.gpu_count,
    -workload.constraint_count,
    -workload.duration_hours,
    workload.preemptible,
)
```


## 12. Explanation Engine

### Accepted Example

```text
Placed llama70b-prod on h100-a-01 and h100-a-02.

Reasons:
- Both nodes provide H100 80GB GPUs.
- The 72GB HBM requirement is satisfied.
- The workload stays inside one InfiniBand domain.
- Each node provides eight free GPUs.
- No maintenance or reservation conflicts exist.
- Placement adds zero stranded GPUs.
- One additional two-node H100 block remains available.
```

### Rejected Example

```text
Rejected llama70b-prod.

Blocking constraints:
- No two H100 nodes with eight free GPUs each are available in one InfiniBand domain.
- Rack A contains one eligible node.
- Rack B contains one eligible node, but cross-rack placement is disabled.
- The next feasible reservation window begins on August 12, 2026.
```


## 13. API Design

### Fleet

```text
POST   /api/v1/fleets
GET    /api/v1/fleets
GET    /api/v1/fleets/{fleet_id}
PUT    /api/v1/fleets/{fleet_id}
DELETE /api/v1/fleets/{fleet_id}
POST   /api/v1/fleets/{fleet_id}/import
GET    /api/v1/fleets/{fleet_id}/summary
GET    /api/v1/fleets/{fleet_id}/topology
GET    /api/v1/fleets/{fleet_id}/fragmentation
GET    /api/v1/fleets/{fleet_id}/contiguous-blocks
```

### Workloads

```text
POST   /api/v1/workloads
GET    /api/v1/workloads
GET    /api/v1/workloads/{workload_id}
PUT    /api/v1/workloads/{workload_id}
DELETE /api/v1/workloads/{workload_id}
POST   /api/v1/workloads/import
```

### Placement

```text
POST   /api/v1/placement/evaluate
POST   /api/v1/placement/run
GET    /api/v1/placement/runs
GET    /api/v1/placement/runs/{run_id}
GET    /api/v1/placement/runs/{run_id}/allocations
GET    /api/v1/placement/runs/{run_id}/rejections
```

### Scenarios

```text
POST   /api/v1/scenarios
GET    /api/v1/scenarios
GET    /api/v1/scenarios/{scenario_id}
POST   /api/v1/scenarios/{scenario_id}/run
DELETE /api/v1/scenarios/{scenario_id}
```

### Benchmarks and Exports

```text
POST   /api/v1/benchmarks/run
GET    /api/v1/benchmarks/{benchmark_id}
GET    /api/v1/benchmarks/{benchmark_id}/report
GET    /api/v1/placement/runs/{run_id}/export/json
GET    /api/v1/placement/runs/{run_id}/export/csv
GET    /api/v1/placement/runs/{run_id}/export/kubernetes
GET    /api/v1/placement/runs/{run_id}/export/slurm
```


## 14. User Interface

Helios should look like a restrained enterprise planning product.

### Design

- Deep navy navigation
- White data surfaces
- Light neutral background
- Restrained blue accent
- Amber warnings
- Controlled red for hard conflicts
- Muted green for feasible placements
- Compact tables
- Minimal chart decoration
- Clear timestamps and status labels

### Navigation

- Overview
- Fleet
- Workloads
- Placement
- Scenarios
- Benchmarks
- Settings

### Overview KPIs

- Healthy GPUs
- Allocated GPUs
- Raw Free GPUs
- Stranded GPUs
- Fragmented GPUs
- Contiguous Eight-GPU Blocks
- Pending Workloads
- Placement Success Rate

### Fleet Page

Table columns:

- Cluster
- Region
- Accelerator
- Nodes
- Healthy GPUs
- Allocated GPUs
- Reserved GPUs
- Raw Free GPUs
- Stranded GPUs
- Contiguous Blocks
- Status

A node drawer shows GPU model, HBM, free GPUs, topology domains, tenant, allocations, reservations, and maintenance.

### Workloads Page

Table columns:

- Workload
- Tenant
- GPU Type
- GPU Count
- Node Shape
- Start
- End
- Priority
- Topology
- Status

### Placement Page

Controls:

- Fleet
- Workload set
- Strategy
- Runtime mode
- Objective weights
- Include allocations
- Include reservations
- Include maintenance

Results:

- Accepted workloads
- Rejected workloads
- Utilization
- Stranded GPUs
- Fragmented GPUs
- Contiguous blocks
- Cross-rack placements
- Runtime

### Scenario Studio

Actions:

- Add or remove workload
- Delay workload
- Add or fail node
- Drain rack
- Extend reservation
- Modify topology requirement
- Modify tenant isolation
- Change priority

### Benchmarks Page

Inputs:

- Fleet size
- Workload count
- Workload mix
- Random seed
- Strategies
- Runtime mode


## 15. Synthetic Fleet Generator

### Profiles

```text
Small:      2 clusters,   8 nodes,  48 GPUs
Medium:     4 clusters,  32 nodes, 192 GPUs
Enterprise: 8 clusters, 128 nodes, 768 GPUs
```

### Suggested Accelerator Mix

```text
H100 80GB: 40%
A100 80GB: 25%
H200:      15%
L40S:      15%
B200:       5%
```

### Node Shapes

- Eight-GPU training nodes
- Four-GPU inference nodes
- Two-GPU development nodes

Generated fleets must include multiple racks, fabric domains, maintenance windows, unhealthy nodes, active allocations, and future reservations.


## 16. Synthetic Workload Generator

### Large Training
- 32 to 128 GPUs
- strict InfiniBand requirement
- contiguous nodes
- long duration
- high priority

### Fine-Tuning
- 4 to 16 GPUs
- moderate topology constraints
- medium duration

### Real-Time Inference
- 2 to 8 GPUs
- tenant isolation
- high availability
- long duration

### Batch Inference
- 1 to 8 GPUs
- flexible placement
- preemptible

### Embeddings
- 1 to 4 GPUs
- medium duration
- moderate priority

### Experimentation
- 1 to 2 GPUs
- short duration
- preemptible


## 17. Discrete-Event Simulator

Events:

- workload arrival,
- workload completion,
- reservation start,
- reservation expiration,
- node failure,
- node recovery,
- maintenance start,
- maintenance end,
- migration,
- preemption.

Simulation loop:

```text
1. Advance to the next event.
2. Apply the event to fleet state.
3. Collect pending workloads.
4. Run the selected placement strategy.
5. Persist allocations and rejections.
6. Calculate metrics.
7. Continue until the simulation ends.
```

Example configuration:

```yaml
simulation:
  start: 2026-08-01T00:00:00Z
  duration_days: 90
  random_seed: 42
  workload_arrivals_per_day: 20
  node_failure_probability_per_day: 0.002
  average_failure_duration_hours: 6
  maintenance_events_per_month: 4
  optimizer_runtime_mode: balanced
```


## 18. Benchmark Methodology

### Required Scenarios

1. Mixed training and inference fleet
2. Large distributed training demand
3. Inference-heavy multi-tenant fleet
4. Rack-maintenance disruption
5. Future reservation pressure
6. Heterogeneous accelerator fleet

### Metrics

- Workload acceptance rate
- GPU utilization
- Stranded GPUs
- Fragmented GPUs
- Fully free nodes
- Contiguous eight-GPU blocks
- Contiguous 16-GPU groups
- Cross-rack placements
- Workload migrations
- P50 scheduling latency
- P95 scheduling latency
- Solver timeout rate
- SLA-risk events

### Reproducibility

Persist:

- random seed,
- fleet checksum,
- workload checksum,
- strategy,
- objective weights,
- runtime mode,
- optimizer version,
- timestamp.

Required report:

```markdown
| Strategy | Acceptance | Utilization | Stranded GPUs | Fragmented GPUs | 8-GPU Blocks | Cross-Rack | P95 Runtime |
|---|---:|---:|---:|---:|---:|---:|---:|
| First Fit | generated | generated | generated | generated | generated | generated | generated |
| Best Fit | generated | generated | generated | generated | generated | generated | generated |
| Topology Heuristic | generated | generated | generated | generated | generated | generated | generated |
| CP-SAT | generated | generated | generated | generated | generated | generated | generated |
```


## 19. Kubernetes and Slurm Exports

Helios exports recommendations. It does not directly mutate a cluster.

### Kubernetes Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llama70b-prod
spec:
  template:
    spec:
      nodeSelector:
        helios.ai/placement-group: pg-h100-a-01
      tolerations:
        - key: tenant
          operator: Equal
          value: finance
          effect: NoSchedule
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: nvidia.com/gpu.product
                    operator: In
                    values:
                      - NVIDIA-H100-80GB-HBM3
```

### Slurm Example

```bash
#SBATCH --partition=h100
#SBATCH --nodes=2
#SBATCH --gres=gpu:h100:8
#SBATCH --constraint=ib_domain_a
#SBATCH --exclusive
#SBATCH --nodelist=h100-a-01,h100-a-02
```


## 20. Testing Strategy

### Unit Tests

- accelerator compatibility,
- HBM validation,
- reservation overlap,
- maintenance overlap,
- tenant isolation,
- failure-domain constraints,
- candidate generation,
- fragmentation calculation,
- stranded capacity,
- topology scoring,
- workload ordering,
- CP-SAT constraints,
- explanation generation.

### Property-Based Tests

- no node exceeds GPU capacity,
- no workload is assigned twice,
- no accepted placement violates hard constraints,
- assigned GPUs equal demand,
- isolated tenants never share forbidden nodes,
- maintenance-conflicting nodes are never selected.

### Integration Tests

- import fleet,
- import workloads,
- run each strategy,
- compare metrics,
- create scenario,
- export Kubernetes YAML,
- export Slurm directives.

### End-to-End Tests

1. Import demo fleet.
2. Import demo workloads.
3. Run First Fit.
4. Run Topology Heuristic.
5. Compare results.
6. Open workload explanation.
7. Create a node-failure scenario.
8. Export the placement plan.


## 21. Performance Targets

These are development targets, not claims.

### Topology Heuristic

- 256 GPUs and 100 workloads: under 500 ms
- 1,024 GPUs and 500 workloads: under 2 seconds

### CP-SAT

- Fast mode: 1 second
- Balanced mode: 5 seconds
- Thorough mode: 30 seconds

### API

- Fleet summary: under 200 ms
- Single workload feasibility: under 500 ms
- Medium scenario comparison: under 2 seconds


## 22. CI/CD and Deployment

### Backend Workflow

```text
ruff
mypy
pytest
coverage
docker build
```

### Frontend Workflow

```text
eslint
TypeScript check
vitest
Playwright smoke test
Next.js build
docker build
```

### Benchmark Workflow

1. Seed deterministic fleet.
2. Generate deterministic workloads.
3. Run all strategies.
4. Export JSON and CSV.
5. Generate Markdown report.
6. Upload artifacts.

### Docker Compose

Services:

```text
web
api
worker
postgres
redis
```

Start:

```bash
cp .env.example .env
docker compose up --build
```

URLs:

```text
Web:      http://localhost:3000
API:      http://localhost:8000
API Docs: http://localhost:8000/docs
```


## 23. Delivery Milestones

### Milestone 1 — Foundation
- Repository setup
- Database schema
- Fleet and workload import
- Basic API
- Frontend shell

### Milestone 2 — Feasibility
- Hard constraints
- Candidate generation
- Placement explanations
- Workload evaluation UI

### Milestone 3 — Baselines
- First Fit
- Best Fit
- Placement metrics
- Initial benchmark

### Milestone 4 — Topology Heuristic
- Topology scoring
- Fragmentation penalties
- Contiguous-block preservation
- Strategy comparison UI

### Milestone 5 — CP-SAT
- Decision variables
- Capacity constraints
- Topology constraints
- Configurable objective
- Timeout handling

### Milestone 6 — Simulator
- Event model
- Workload arrivals
- Failures
- Maintenance
- Reservations
- 90-day replay

### Milestone 7 — Scenario Studio
- Fleet changes
- Workload changes
- Baseline comparison
- Exports

### Milestone 8 — Portfolio Polish
- Corporate UI
- Screenshots
- Benchmark report
- Architecture diagram
- Demo video
- CI and documentation


## 24. Acceptance Criteria

Helios is complete when a reviewer can:

1. Start it with one command.
2. Import a fleet.
3. Import workloads.
4. Evaluate one workload.
5. Run First Fit.
6. Run Best Fit.
7. Run the Topology-Aware Heuristic.
8. Run CP-SAT.
9. Compare all strategies.
10. Inspect accepted and rejected workloads.
11. Read placement explanations.
12. View fragmentation and stranded capacity.
13. Run maintenance and failure scenarios.
14. Export Kubernetes and Slurm recommendations.
15. Reproduce benchmark results from a fixed seed.
16. Run the test suite successfully.


## 25. Resume-Ready Entry

### Helios — Topology-Aware GPU Placement Optimizer | Python, FastAPI, OR-Tools, NetworkX, PostgreSQL, Next.js

- Built a constraint-based GPU placement engine that mapped training and inference workloads onto heterogeneous accelerator fleets using GPU type, HBM, node shape, reservation duration, priority, tenancy, and SLA requirements.

- Modeled NVLink, NVSwitch, InfiniBand, rack, maintenance, reservation, and failure-domain constraints to preserve high-bandwidth locality and contiguous capacity for distributed workloads.

- Implemented First Fit, Best Fit, topology-aware heuristic, and OR-Tools CP-SAT strategies, benchmarking workload acceptance, utilization, stranded GPUs, fragmented capacity, cross-rack placement, and scheduling latency.

- Developed a discrete-event simulator for workload arrivals, reservation expirations, node failures, and maintenance drains, producing reproducible 90-day allocation benchmarks and placement recommendations.


## 26. Final Portfolio Standard

The finished repository should include:

- polished README,
- architecture diagram,
- six consistent screenshots,
- seeded demo fleet,
- seeded workload set,
- generated benchmark report,
- reproducible setup,
- tests,
- CI,
- Docker Compose,
- and a short demo video.

A reviewer should understand in under two minutes that Helios solves placement, not workload sizing. They should then be able to run the application, compare algorithms, inspect explanations, and reproduce benchmark results.
