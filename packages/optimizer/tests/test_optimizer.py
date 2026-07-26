from datetime import UTC, datetime, timedelta

import pytest
from helios_optimizer import (
    Candidate,
    Cluster,
    Fleet,
    Node,
    Rack,
    Workload,
    best_fit,
    calculate,
    check_candidate,
    cpsat,
    first_fit,
    generate_candidates,
    topology_aware,
)
from helios_optimizer.exports import kubernetes_affinity, slurm_constraint, to_json

NOW = datetime(2026, 8, 1, tzinfo=UTC)


def node(id, rack, *, free=8, domain="ib-a", accelerator="H100", maintenance=None):
    return Node(
        id=id,
        cluster_id="c1",
        rack_id=rack,
        accelerator_class=accelerator,
        gpu_count=8,
        hbm_per_gpu_gb=80,
        cpu_cores=192,
        system_memory_gb=2048,
        local_storage_tb=15,
        nvlink_domain=id,
        nvswitch_domain=rack,
        infiniband_domain=domain,
        allocated_gpus=8 - free,
        maintenance_status=maintenance or "available",
    )


def workload(id="w", *, count=8, per_node=8, **kwargs):
    return Workload(
        id=id,
        accelerator_class="H100",
        gpu_count=count,
        gpus_per_node=per_node,
        node_count=count // per_node,
        start_time=NOW,
        end_time=NOW + timedelta(days=1),
        **kwargs,
    )


def fleet():
    return Fleet(
        nodes=(node("a1", "a"), node("a2", "a"), node("b1", "b")),
        clusters=(Cluster("c1", storage_tier="nvme"),),
        racks=(Rack("a", "c1", failure_domain="fd-a"), Rack("b", "c1", failure_domain="fd-b")),
    )


def test_workload_validates_shape():
    with pytest.raises(ValueError):
        workload(count=7, per_node=4)


def test_candidate_generation_prefers_exact_fit_and_topology():
    candidates = generate_candidates(workload(count=16), fleet())
    assert candidates[0].node_ids == ("a1", "a2")
    assert candidates[0].locality == 1
    assert candidates[0].exact_fit


def test_feasibility_enforces_rack_local():
    w = workload(count=16, rack_local_required=True)
    c = Candidate(w.id, ("a1", "b1"), (("a1", 8), ("b1", 8)))
    result = check_candidate(c, w, fleet())
    assert not result.feasible
    assert "rack_local" in result.blocking_constraints


def test_greedy_strategies_update_capacity_and_reject_overflow():
    workloads = (workload("high", priority=10), workload("low"), workload("overflow"))
    result = first_fit(Fleet(nodes=(node("a1", "a"), node("a2", "a"))), workloads)
    assert [a.workload_id for a in result.allocations] == ["high", "low"]
    assert result.rejections[0].workload_id == "overflow"
    assert calculate(result.fleet).raw_free_gpus == 0


def test_best_fit_uses_smallest_remaining_capacity():
    state = Fleet(nodes=(node("big", "a", free=8), node("small", "b", free=4)))
    result = best_fit(state, (workload(per_node=4, count=4),))
    assert result.allocations[0].assigned_nodes == ("small",)


def test_topology_aware_keeps_multi_node_workload_local():
    result = topology_aware(fleet(), (workload(count=16),))
    assert result.allocations[0].assigned_nodes == ("a1", "a2")
    assert not result.allocations[0].cross_rack


def test_cpsat_or_fallback_returns_valid_result():
    result = cpsat(fleet(), (workload(),), mode="fast")
    assert len(result.allocations) == 1
    assert result.strategy in {"cpsat", "cpsat_fallback"}


def test_exports():
    result = first_fit(fleet(), (workload(),))
    allocation = result.allocations[0]
    assert '"accepted_workloads": 1' in to_json(result)
    assert kubernetes_affinity(allocation)["nodeAffinity"]
    assert slurm_constraint(allocation).startswith("--nodelist=")
