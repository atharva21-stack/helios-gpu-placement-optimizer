"""Portable result serializers and scheduler recommendations."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict

from .domain import Allocation, PlacementResult
from .metrics import result_metrics


def to_dict(result: PlacementResult) -> dict:
    return {
        "strategy": result.strategy,
        "runtime_ms": result.runtime_ms,
        "objective_value": result.objective_value,
        "allocations": [asdict(value) for value in result.allocations],
        "rejections": [asdict(value) for value in result.rejections],
        "metrics": result_metrics(result),
    }


def to_json(result: PlacementResult, *, indent: int = 2) -> str:
    return json.dumps(to_dict(result), indent=indent, default=str)


def to_csv(result: PlacementResult) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=("workload_id", "strategy", "assigned_nodes", "cross_rack", "score"),
    )
    writer.writeheader()
    for allocation in result.allocations:
        writer.writerow(
            {
                "workload_id": allocation.workload_id,
                "strategy": allocation.strategy,
                "assigned_nodes": ",".join(allocation.assigned_nodes),
                "cross_rack": allocation.cross_rack,
                "score": allocation.score,
            }
        )
    return output.getvalue()


def kubernetes_affinity(allocation: Allocation) -> dict:
    return {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {
                                "key": "kubernetes.io/hostname",
                                "operator": "In",
                                "values": list(allocation.assigned_nodes),
                            }
                        ]
                    }
                ]
            }
        }
    }


def slurm_constraint(allocation: Allocation) -> str:
    return f"--nodelist={','.join(allocation.assigned_nodes)}"
