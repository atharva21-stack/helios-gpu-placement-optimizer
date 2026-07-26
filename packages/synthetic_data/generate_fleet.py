"""Deterministic synthetic fleet generator."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

PROFILES = {"small": (2, 8), "medium": (4, 32), "enterprise": (8, 128)}
ACCELERATORS = [
    ("H100_80GB", 80),
    ("A100_80GB", 80),
    ("H200_141GB", 141),
    ("L40S_48GB", 48),
    ("B200_192GB", 192),
]


def generate_fleet(profile: str = "small", seed: int = 42) -> dict[str, list[dict]]:
    cluster_count, node_count = PROFILES[profile]
    rng = random.Random(seed)
    clusters = [
        {
            "id": f"cluster-{index + 1}",
            "name": f"GPU Cluster {index + 1}",
            "region_id": "us-central",
            "network_fabric": "infiniband",
            "storage_tier": "nvme",
            "status": "active",
        }
        for index in range(cluster_count)
    ]
    racks: list[dict] = []
    for cluster in clusters:
        for rack_index in range(2):
            racks.append(
                {
                    "id": f"{cluster['id']}-rack-{rack_index + 1}",
                    "cluster_id": cluster["id"],
                    "failure_domain": f"{cluster['id']}-fd-{rack_index + 1}",
                    "network_domain": f"{cluster['id']}-ib",
                    "power_domain": f"{cluster['id']}-power-{rack_index + 1}",
                }
            )
    nodes = []
    weights = [40, 25, 15, 15, 5]
    for index in range(node_count):
        cluster = clusters[index % cluster_count]
        rack = racks[(index % cluster_count) * 2 + ((index // cluster_count) % 2)]
        accelerator, hbm = rng.choices(ACCELERATORS, weights=weights, k=1)[0]
        gpu_count = rng.choices([8, 4, 2], weights=[60, 25, 15], k=1)[0]
        nodes.append(
            {
                "id": f"gpu-node-{index + 1:03d}",
                "cluster_id": cluster["id"],
                "rack_id": rack["id"],
                "accelerator_class": accelerator,
                "gpu_count": gpu_count,
                "hbm_per_gpu_gb": hbm,
                "cpu_cores": 24 * gpu_count,
                "system_memory_gb": 256 * gpu_count,
                "local_storage_tb": 2 * gpu_count,
                "nvlink_domain": f"nv-{index + 1:03d}",
                "nvswitch_domain": f"nvs-{index + 1:03d}" if gpu_count == 8 else None,
                "infiniband_domain": rack["network_domain"],
                "network_bandwidth_gbps": 400,
                "health_status": "unhealthy" if rng.random() < 0.02 else "healthy",
                "maintenance_status": "available",
            }
        )
    return {
        "regions": [{"id": "us-central", "name": "US Central", "country": "US"}],
        "clusters": clusters,
        "racks": racks,
        "nodes": nodes,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=PROFILES, default="small")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(generate_fleet(args.profile, args.seed), indent=2)
    if args.output:
        args.output.write_text(payload + "\n")
    else:
        print(payload)
