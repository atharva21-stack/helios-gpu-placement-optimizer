"""Human-readable placement rationale."""

from __future__ import annotations

from .domain import Candidate, Fleet, Workload


def explain_placement(candidate: Candidate, workload: Workload, fleet: Fleet) -> tuple[str, ...]:
    nodes = [fleet.node_map()[node_id] for node_id in candidate.node_ids]
    reasons = [
        f"Placed {workload.id} on {', '.join(candidate.node_ids)}.",
        f"All nodes provide {workload.accelerator_class} GPUs with sufficient HBM.",
        f"Each node provides {workload.gpus_per_node} free GPUs.",
        "No maintenance or reservation conflicts exist.",
    ]
    if candidate.locality == 1:
        reasons.append("The placement stays inside one NVSwitch domain.")
    elif len({node.rack_id for node in nodes}) == 1:
        reasons.append("The placement stays inside one rack.")
    elif len({node.infiniband_domain for node in nodes}) == 1:
        reasons.append("The placement stays inside one InfiniBand domain.")
    if candidate.exact_fit:
        reasons.append("The placement is an exact fit and leaves no partial nodes.")
    return tuple(reasons)


def explain_rejection(workload: Workload, reasons: tuple[str, ...]) -> tuple[str, ...]:
    return (f"Could not place {workload.id}.",) + reasons
