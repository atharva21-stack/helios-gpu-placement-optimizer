"""Deterministic workload generator."""

from __future__ import annotations

import argparse
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path


def generate_workloads(count: int = 20, seed: int = 42) -> dict[str, list[dict]]:
    rng = random.Random(seed)
    start = datetime(2026, 8, 1, tzinfo=UTC)
    shapes = [
        ("training", "H100_80GB", 8, 8, True),
        ("fine_tuning", "A100_80GB", 4, 4, False),
        ("inference", "H100_80GB", 2, 2, False),
        ("embeddings", "L40S_48GB", 2, 2, False),
        ("experimentation", "H100_80GB", 1, 1, False),
    ]
    workloads = []
    for index in range(count):
        kind, accelerator, gpu_count, per_node, ib_required = rng.choice(shapes)
        arrival = start + timedelta(hours=rng.randint(0, 14 * 24))
        duration = timedelta(hours=rng.randint(4, 14 * 24))
        workloads.append(
            {
                "id": f"workload-{index + 1:04d}",
                "name": f"{kind.replace('_', ' ').title()} {index + 1}",
                "tenant_id": f"tenant-{rng.randint(1, 5)}",
                "workload_type": kind,
                "priority": rng.randint(10, 100),
                "accelerator_class": accelerator,
                "gpu_count": gpu_count,
                "gpus_per_node": per_node,
                "node_count": 1,
                "hbm_required_per_gpu_gb": 40,
                "start_time": arrival.isoformat(),
                "end_time": (arrival + duration).isoformat(),
                "infiniband_required": ib_required,
                "preemptible": kind in {"embeddings", "experimentation"},
            }
        )
    return {"workloads": workloads}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(generate_workloads(args.count, args.seed), indent=2)
    if args.output:
        args.output.write_text(payload + "\n")
    else:
        print(payload)
