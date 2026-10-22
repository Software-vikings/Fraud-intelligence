from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_analyze():
    payload = {"transaction_id":"T1","customer_id":"C1","card_id":"K1","amount":100,
               "merchant_category":"groceries","merchant_id":"M1","country":"ES","home_country":"ES",
               "transaction_timestamp":"2026-01-01T10:00:00","customer_avg_amount_30d":50}
    response = client.post("/analyze",json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "APPROVE"
