from fastapi.testclient import TestClient
from helios_api.main import app
from helios_api.store import store

client = TestClient(app)


def setup_function():
    store.fleets.clear()
    store.workloads.clear()
    store.runs.clear()


def fleet():
    return {
        "nodes": [
            {
                "id": "h100-a-01",
                "cluster_id": "prod",
                "rack_id": "rack-a",
                "accelerator_class": "H100_80GB",
                "gpu_count": 8,
                "hbm_per_gpu_gb": 80,
                "nvlink_domain": "nv-a",
                "infiniband_domain": "ib-a",
            },
            {
                "id": "h100-a-02",
                "cluster_id": "prod",
                "rack_id": "rack-a",
                "accelerator_class": "H100_80GB",
                "gpu_count": 8,
                "hbm_per_gpu_gb": 80,
                "nvlink_domain": "nv-b",
                "infiniband_domain": "ib-a",
            },
        ]
    }


def workload(workload_id="train"):
    return {
        "id": workload_id,
        "accelerator_class": "H100_80GB",
        "gpu_count": 16,
        "gpus_per_node": 8,
        "node_count": 2,
        "hbm_required_per_gpu_gb": 72,
        "infiniband_required": True,
    }


def test_health_and_fleet_summary():
    assert client.get("/health").json() == {"status": "ok"}
    response = client.post("/api/v1/fleets/demo/import", json=fleet())
    assert response.status_code == 201
    assert response.json() == {
        "fleet_id": "demo",
        "nodes": 2,
        "total_gpus": 16,
        "available_gpus": 16,
        "accelerators": {"H100_80GB": 16},
        "racks": 1,
        "clusters": 1,
    }


def test_evaluate_and_run_retrieval():
    client.post("/api/v1/fleets/demo/import", json=fleet())
    assert client.post("/api/v1/workloads/import", json={"workloads": [workload()]}).json() == {
        "imported": 1
    }
    evaluation = client.post(
        "/api/v1/placement/evaluate",
        json={"fleet_id": "demo", "workload_id": "train"},
    )
    assert evaluation.status_code == 200
    assert evaluation.json()["feasible"] is True
    run = client.post(
        "/api/v1/placement/run",
        json={"fleet_id": "demo", "workload_ids": ["train"], "strategy": "best_fit"},
    )
    assert run.status_code == 201
    body = run.json()
    assert body["accepted_workloads"] == 1
    assert body["fleet_utilization"] == 1
    assert client.get(f"/api/v1/placement/runs/{body['id']}").json()["id"] == body["id"]
    assert len(client.get(f"/api/v1/placement/runs/{body['id']}/allocations").json()) == 1


def test_rejection_and_not_found():
    client.post("/api/v1/fleets/demo/import", json=fleet())
    impossible = workload("impossible") | {
        "accelerator_class": "B200",
        "gpu_count": 8,
        "node_count": 1,
    }
    response = client.post(
        "/api/v1/placement/evaluate",
        json={"fleet_id": "demo", "workload": impossible},
    )
    assert response.json()["feasible"] is False
    assert "B200" in response.json()["reasons"][0]
    assert client.get("/api/v1/placement/runs/missing").status_code == 404
