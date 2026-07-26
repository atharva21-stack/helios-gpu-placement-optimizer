from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from helios_optimizer import Fleet, PlacementResult, Workload, topology_aware

from .events import Event, EventType

Strategy = Callable[[Fleet, tuple[Workload, ...]], PlacementResult]


@dataclass(frozen=True)
class SimulationResult:
    fleet: Fleet
    placement_results: tuple[PlacementResult, ...]
    processed_events: tuple[Event, ...]

    @property
    def accepted_workloads(self) -> int:
        return sum(len(result.allocations) for result in self.placement_results)


def _node_status(fleet: Fleet, node_id: str, **changes: object) -> Fleet:
    return replace(
        fleet,
        nodes=tuple(
            replace(node, **changes) if node.id == node_id else node for node in fleet.nodes
        ),
    )


def run_simulation(
    fleet: Fleet,
    workloads: tuple[Workload, ...],
    events: tuple[Event, ...] = (),
    strategy: Strategy = topology_aware,
) -> SimulationResult:
    """Replay events and schedule arrivals in timestamp order.

    Workloads without an explicit arrival event are scheduled at their declared
    start time. Capacity release is represented by a fresh simulation snapshot
    in this MVP; explicit completion events are retained in the audit timeline.
    """
    by_id = {workload.id: workload for workload in workloads}
    arrivals = {event.target_id for event in events if event.type == EventType.WORKLOAD_ARRIVAL}
    timeline = list(events)
    timeline.extend(
        Event(workload.start_time, EventType.WORKLOAD_ARRIVAL, workload.id)
        for workload in workloads
        if workload.id not in arrivals
    )
    state = fleet
    results: list[PlacementResult] = []
    processed: list[Event] = []
    for event in sorted(timeline):
        if event.type == EventType.NODE_FAILURE:
            state = _node_status(state, event.target_id, health_status="unhealthy")
        elif event.type == EventType.NODE_RECOVERY:
            state = _node_status(state, event.target_id, health_status="healthy")
        elif event.type == EventType.MAINTENANCE_START:
            state = _node_status(state, event.target_id, maintenance_status="maintenance")
        elif event.type == EventType.MAINTENANCE_END:
            state = _node_status(state, event.target_id, maintenance_status="available")
        elif event.type == EventType.WORKLOAD_ARRIVAL and event.target_id in by_id:
            result = strategy(state, (by_id[event.target_id],))
            results.append(result)
            state = result.fleet
        processed.append(event)
    return SimulationResult(state, tuple(results), tuple(processed))
