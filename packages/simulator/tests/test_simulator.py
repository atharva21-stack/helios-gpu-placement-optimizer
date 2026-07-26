from datetime import UTC, datetime, timedelta

from helios_optimizer import Fleet, Node, Workload
from helios_simulator import Event, EventType, run_simulation

NOW = datetime(2026, 8, 1, tzinfo=UTC)


def test_failure_before_arrival_rejects_workload():
    fleet = Fleet(
        nodes=(
            Node(
                id="n1",
                cluster_id="c1",
                rack_id="r1",
                accelerator_class="H100",
                gpu_count=8,
                hbm_per_gpu_gb=80,
            ),
        )
    )
    workload = Workload(
        id="w1",
        accelerator_class="H100",
        gpu_count=8,
        gpus_per_node=8,
        node_count=1,
        start_time=NOW + timedelta(hours=1),
        end_time=NOW + timedelta(days=1),
    )
    result = run_simulation(
        fleet,
        (workload,),
        (Event(NOW, EventType.NODE_FAILURE, "n1"),),
    )
    assert result.accepted_workloads == 0
    assert result.placement_results[0].rejections[0].workload_id == "w1"
