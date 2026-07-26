#!/usr/bin/env python3
"""Run all placement strategies against the checked-in demo inputs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import yaml
from helios_optimizer import (
    Cluster,
    Fleet,
    Node,
    Rack,
    Workload,
    best_fit,
    cpsat,
    first_fit,
    result_metrics,
    topology_aware,
)

ROOT = Path(__file__).resolve().parents[1]


def load_demo() -> tuple[Fleet, tuple[Workload, ...]]:
    fleet_data = yaml.safe_load((ROOT / "examples/fleet-small.yaml").read_text())
    workload_data = yaml.safe_load((ROOT / "examples/workloads-demo.yaml").read_text())
    clusters = tuple(
        Cluster(
            id=item["id"],
            region_id=item.get("region_id", ""),
            name=item.get("name", ""),
            network_fabric=item.get("network_fabric", ""),
            storage_tier=item.get("storage_tier", ""),
            status=item.get("status", "active"),
        )
        for item in fleet_data["clusters"]
    )
    racks = tuple(
        Rack(
            id=item["id"],
            cluster_id=item["cluster_id"],
            failure_domain=item.get("failure_domain", ""),
            network_domain=item.get("network_domain", ""),
            power_domain=item.get("power_domain", ""),
        )
        for item in fleet_data["racks"]
    )
    nodes = tuple(Node(**item) for item in fleet_data["nodes"])
    fleet = Fleet(nodes=nodes, clusters=clusters, racks=racks)
    def timestamp(value: str | datetime) -> datetime:
        return value if isinstance(value, datetime) else datetime.fromisoformat(value)

    workloads = tuple(
        Workload(
            **{
                **item,
                "start_time": timestamp(item["start_time"]),
                "end_time": timestamp(item["end_time"]),
            }
        )
        for item in workload_data["workloads"]
    )
    return fleet, workloads


def main() -> None:
    fleet, workloads = load_demo()
    strategies = {
        "first_fit": first_fit,
        "best_fit": best_fit,
        "topology_aware": topology_aware,
        "cpsat": lambda state, items: cpsat(state, items, mode="fast"),
    }
    report = {
        name: result_metrics(strategy(fleet, workloads)) for name, strategy in strategies.items()
    }
    output_dir = ROOT / "benchmark-results"
    output_dir.mkdir(exist_ok=True)
    output = output_dir / "demo.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"Wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
