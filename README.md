# Helios

Helios is a topology-aware GPU placement planner. It maps declared AI workload
requirements onto a heterogeneous fleet while preserving useful contiguous
capacity. It is a recommendation and simulation engine—not a Kubernetes or
Slurm scheduler and not a workload-sizing calculator.

## What works

- Fleet and workload import from JSON/YAML-compatible documents
- Accelerator, HBM, node-shape, health, maintenance, topology, reservation,
  tenancy, and failure-domain feasibility checks
- First Fit, Best Fit, topology-aware, and CP-SAT placement strategies
- Placement explanations, fragmentation and contiguous-capacity metrics
- Kubernetes and Slurm recommendation exports
- Deterministic demo data and benchmark runner
- FastAPI service and a Next.js operations dashboard

## Quick start

Requires Python 3.11+ and Node 20+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,solver]"
pytest
make api
```

In another terminal:

```bash
cd apps/web
npm install
npm run dev
```

Open the dashboard at `http://localhost:3000` and API documentation at
`http://localhost:8000/docs`.

Run a deterministic CLI comparison:

```bash
python scripts/run_benchmarks.py
```

Docker users can run `docker compose up --build`.

## Architecture

```text
Next.js dashboard -> FastAPI API -> optimizer strategies
                                      |
                   YAML/JSON -> domain + feasibility
                                      |
                               simulator / exports
```

The optimizer package is intentionally independent of FastAPI and storage, so
it can be embedded in batch jobs or schedulers. The MVP API uses an in-memory
repository; production deployments can replace that boundary with PostgreSQL
and a background queue without changing placement logic.

See [plan.md](plan.md) for the complete product specification and
[docs/architecture.md](docs/architecture.md) for design details.
