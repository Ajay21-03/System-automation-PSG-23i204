"""API endpoint smoke tests."""
import json
import pytest


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True


def test_dashboard_summary_no_dataset(client):
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200


def test_fleet_no_dataset(client):
    res = client.get("/api/fleet")
    assert res.status_code == 200


def test_predict_missing_fields(client):
    res = client.post("/api/predict",
                      data=json.dumps({"temperature": 55.0}),
                      content_type="application/json")
    assert res.status_code in (422, 503)


def test_dataset_generate(client):
    res = client.post("/api/dataset/generate",
                      data=json.dumps({"rows": 100}),
                      content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["data"]["rows"] == 100


def test_dataset_validate(client):
    res = client.get("/api/dataset/validate")
    assert res.status_code == 200


def test_model_train(client):
    # First generate a small dataset
    client.post("/api/dataset/generate",
                data=json.dumps({"rows": 500}),
                content_type="application/json")
    res = client.post("/api/model/train")
    assert res.status_code == 200
    data = res.get_json()
    assert "accuracy" in data["data"]


def test_predict_after_training(client):
    payload = {
        "temperature": 55.0, "pressure": 4.5, "vibration": 1.5,
        "rpm": 1800.0, "current": 7.0, "torque": 40.0
    }
    res = client.post("/api/predict",
                      data=json.dumps(payload),
                      content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert "predicted_class" in data["data"]


def test_decisions_evaluate_emergency(client):
    payload = {
        "temperature": 97.0, "pressure": 9.8, "vibration": 8.0,
        "rpm": 3500.0, "current": 17.0, "torque": 116.0,
        "machine_id": "TEST-EMERG"
    }
    res = client.post("/api/decisions/evaluate",
                      data=json.dumps(payload),
                      content_type="application/json")
    assert res.status_code == 200
    assert res.get_json()["data"]["decision"] == "EMERGENCY_STOP"


def test_decisions_demo(client):
    res = client.get("/api/decisions/demo")
    assert res.status_code == 200
    demos = res.get_json()["data"]
    assert "EMERGENCY_STOP" in demos


def test_maintenance_list(client):
    res = client.get("/api/maintenance")
    assert res.status_code == 200


def test_maintenance_create_and_update(client):
    create_res = client.post("/api/maintenance",
                             data=json.dumps({
                                 "machine_id": "ARM-TEST",
                                 "decision":   "SCHEDULE_MAINTENANCE",
                                 "severity":   "warning",
                                 "description":"Test case"
                             }),
                             content_type="application/json")
    assert create_res.status_code in (200, 201)
    data = create_res.get_json()["data"]
    case_id = data.get("id")
    if case_id:
        update_res = client.patch(f"/api/maintenance/{case_id}",
                                  data=json.dumps({"status": "acknowledged"}),
                                  content_type="application/json")
        assert update_res.status_code == 200


def test_maintenance_invalid_status(client):
    res = client.patch("/api/maintenance/999999",
                       data=json.dumps({"status": "invalid_status"}),
                       content_type="application/json")
    assert res.status_code == 422


def test_security_simulate(client):
    res = client.post("/api/security/simulate",
                      data=json.dumps({"arm_id": "ARM-001", "joint": "shoulder"}),
                      content_type="application/json")
    assert res.status_code == 200


def test_logs_endpoint(client):
    res = client.get("/api/logs")
    assert res.status_code == 200


def test_automation_rules(client):
    res = client.get("/api/automation/rules")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "rules" in data
    assert len(data["rules"]) > 0


def test_system_status(client):
    res = client.get("/api/system/status")
    assert res.status_code == 200
