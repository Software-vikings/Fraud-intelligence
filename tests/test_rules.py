from src.engine.rules import evaluate_transaction

def sample(**overrides):
    tx = {"transaction_id":"T1","customer_id":"C1","card_id":"K1","amount":100,
          "merchant_category":"groceries","country":"ES","home_country":"ES",
          "transaction_timestamp":"2026-01-01T10:00:00","failed_attempts_24h":0,
          "customer_avg_amount_30d":50}
    tx.update(overrides)
    return tx

def test_low_risk_approved():
    assert evaluate_transaction(sample())["decision"] == "APPROVE"

def test_high_amount_triggers_rule():
    result = evaluate_transaction(sample(amount=1000))
    assert "R001" in [x["rule_id"] for x in result["triggered_rules"]]

def test_foreign_country_triggers_rule():
    result = evaluate_transaction(sample(country="FR"))
    assert "R003" in [x["rule_id"] for x in result["triggered_rules"]]

def test_multiple_rules_can_decline():
    result = evaluate_transaction(sample(amount=2000,country="FR",failed_attempts_24h=4,merchant_category="crypto"))
    assert result["decision"] == "DECLINE"
    assert len(result["triggered_rules"]) >= 3

def test_velocity_rule():
    history = [{"card_id":"K1","transaction_timestamp":f"2026-01-01T09:5{i}:00"} for i in range(4)]
    result = evaluate_transaction(sample(transaction_timestamp="2026-01-01T10:00:00"),history=history)
    assert "R002" in [x["rule_id"] for x in result["triggered_rules"]]
