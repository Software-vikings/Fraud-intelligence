import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def generate_demo_dataset():
    """Make endpoint tests reproducible in a clean checkout."""
    from scripts.generate_data import main as generate_data
    from scripts.run_evaluation import main as run_evaluation

    generate_data()
    run_evaluation()


def test_operations_console_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "Fraud operations overview" in response.text
    assert "Transaction alert queue" in response.text


def test_dashboard_returns_operational_metrics():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert payload["metrics"]["transaction_count"] == 3000
    assert payload["alert_count"] >= 0
    assert "data_notice" in payload


def test_alert_queue_returns_cases():
    response = client.get("/api/alerts")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 0
    assert isinstance(payload["items"], list)


def test_rule_performance_returns_configured_rules():
    response = client.get("/api/rules/performance")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) >= 1
    assert all("triggers" in rule and "enabled" in rule for rule in payload["items"])


def test_case_detail_has_parsed_rule_explanations():
    queue = client.get("/api/alerts").json()["items"]
    if not queue:
        pytest.skip("The generated sample produced no alerts.")
    response = client.get("/api/cases/" + queue[0]["transaction_id"])
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["triggered_rules"], list)
    assert isinstance(payload["history"], list)


def test_case_action_is_persisted_with_audit_history():
    queue = client.get("/api/alerts").json()["items"]
    if not queue:
        pytest.skip("The generated sample produced no alerts.")
    transaction_id = queue[0]["transaction_id"]
    response = client.post(
        "/api/cases/" + transaction_id,
        json={
            "status": "IN_REVIEW",
            "assigned_to": "QA Analyst",
            "note": "Reviewed transaction context and requested supporting evidence.",
        },
    )
    assert response.status_code == 200
    assert response.json()["case"]["status"] == "IN_REVIEW"
    assert response.json()["case"]["assigned_to"] == "QA Analyst"
    assert len(response.json()["history"]) >= 1
    detail = client.get("/api/cases/" + transaction_id).json()
    assert detail["history"][0]["note"].startswith("Reviewed transaction context")


def test_case_action_rejects_short_investigation_note():
    queue = client.get("/api/alerts").json()["items"]
    if not queue:
        pytest.skip("The generated sample produced no alerts.")
    response = client.post(
        "/api/cases/" + queue[0]["transaction_id"],
        json={"status": "IN_REVIEW", "assigned_to": "QA Analyst", "note": "bad"},
    )
    assert response.status_code == 422
