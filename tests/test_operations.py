from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_operations_console_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "Fraud operations overview" in response.text
    assert "Transaction alert queue" in response.text


def test_dashboard_returns_operational_metrics():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert payload["metrics"]["transaction_count"] >= 1
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
        return
    response = client.get("/api/cases/" + queue[0]["transaction_id"])
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["triggered_rules"], list)
    assert isinstance(payload["history"], list)
