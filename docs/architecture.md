# Architecture

Helios separates fleet planning from the systems that execute placements. Kubernetes and Slurm remain the source of truth for runtime state; Helios consumes snapshots and returns recommendations.

```text
Next.js console
      │ HTTPS / JSON
      ▼
FastAPI service ─── PostgreSQL (inventory, workloads, runs)
      │     └────── Redis + worker queue (long simulations)
      ▼
candidate generation → feasibility → strategy → metrics/explanations
                                              │
                                              └── JSON, CSV, K8s, Slurm exports
```

## Boundaries

- `apps/web` is a read-heavy operations console. It can submit workloads and runs, but contains no optimization logic.
- `apps/api` owns validation, persistence, authorization, and job orchestration.
- `packages/optimizer` is deterministic domain logic with no HTTP or database dependencies.
- `packages/simulator` replays timestamped events over an isolated fleet state.
- PostgreSQL stores durable definitions and results. Redis holds only ephemeral queues, locks, and progress.

## Placement lifecycle

1. The API creates an immutable fleet snapshot and validates requested workloads.
2. Candidate generation removes impossible nodes, groups the remainder by topology, and prunes dominated combinations.
3. The selected strategy assigns candidates against a mutable in-memory snapshot.
4. Metrics are calculated from both pre- and post-placement states.
5. The run and its allocations are committed atomically. Explanations and exports are derived from that stored result.

Every result records the strategy version, input snapshot identifier, configuration, random seed where relevant, timestamps, and runtime. This makes benchmark and incident results reproducible.

## Reliability and scale

Interactive heuristic runs execute inline with a strict timeout. CP-SAT and simulation jobs execute on workers and expose progress through polling. Run creation accepts an idempotency key. Fleet snapshot versions provide optimistic concurrency, and a recommendation is marked stale if the live snapshot advances.

Authorization is tenant-scoped for workloads and reservations, while fleet mutations require an operator role. Sensitive labels are filtered from exports and application logs.
