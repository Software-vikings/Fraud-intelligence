from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any

DEFAULT_RULES = [
    {"id":"R001","name":"Unusually high amount","enabled":True,"severity":"high","score":35,"threshold_multiplier":8.0},
    {"id":"R002","name":"High card transaction velocity","enabled":True,"severity":"high","score":30,"max_transactions":4,"window_minutes":10},
    {"id":"R003","name":"Country differs from home country","enabled":True,"severity":"medium","score":20},
    {"id":"R004","name":"Repeated failed attempts","enabled":True,"severity":"medium","score":20,"min_failed_attempts":3},
    {"id":"R005","name":"High-risk merchant category","enabled":True,"severity":"medium","score":15,"categories":["crypto","cash_equivalent","gambling"]}
]

def evaluate_transaction(tx: dict[str, Any], history: list[dict[str, Any]] | None = None,
                         rules: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Evaluate one transaction and return transparent rule hits and a decision."""
    history = history or []
    rules = rules or DEFAULT_RULES
    hits, score = [], 0
    for rule in rules:
        if not rule.get("enabled", True):
            continue
        rid = rule["id"]
        triggered, reason = False, ""
        if rid == "R001":
            baseline = max(float(tx.get("customer_avg_amount_30d") or 0), 1.0)
            triggered = float(tx.get("amount", 0)) >= baseline * float(rule.get("threshold_multiplier", 8))
            reason = f"Amount {tx.get('amount')} is at least {rule.get('threshold_multiplier', 8)}x the 30-day customer average ({baseline:.2f})."
        elif rid == "R002":
            ts = _parse_time(tx.get("transaction_timestamp"))
            window = int(rule.get("window_minutes", 10))
            recent = 0
            for item in history:
                if item.get("card_id") == tx.get("card_id"):
                    other_ts = _parse_time(item.get("transaction_timestamp"))
                    if other_ts and ts and timedelta(0) <= ts - other_ts <= timedelta(minutes=window):
                        recent += 1
            triggered = recent + 1 > int(rule.get("max_transactions", 4))
            reason = f"{recent + 1} transactions for this card within {window} minutes."
        elif rid == "R003":
            home, country = tx.get("home_country"), tx.get("country")
            triggered = bool(home and country and home.upper() != country.upper())
            reason = f"Transaction country {country} differs from home country {home}."
        elif rid == "R004":
            attempts = int(tx.get("failed_attempts_24h") or 0)
            triggered = attempts >= int(rule.get("min_failed_attempts", 3))
            reason = f"{attempts} failed attempts recorded in the previous 24 hours."
        elif rid == "R005":
            category = str(tx.get("merchant_category", "")).lower()
            triggered = category in [c.lower() for c in rule.get("categories", [])]
            reason = f"Merchant category '{category}' is included in the example high-risk category list."
        if triggered:
            score += int(rule.get("score", 0))
            hits.append({"rule_id":rid,"rule_name":rule["name"],"severity":rule.get("severity","medium"),
                         "score":int(rule.get("score",0)),"reason":reason})
    thresholds = {"review":25,"decline":60}
    if rules and isinstance(rules, dict):
        thresholds = rules.get("decision_thresholds", thresholds)
    decision = "DECLINE" if score >= thresholds["decline"] else "REVIEW" if score >= thresholds["review"] else "APPROVE"
    return {"transaction_id":tx.get("transaction_id"),"risk_score":min(score,100),
            "decision":decision,"triggered_rules":hits,"explanation":" ".join(h["reason"] for h in hits) or "No configured demonstration rule was triggered."}

def _parse_time(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z","+00:00")).replace(tzinfo=None)
    except ValueError:
        return None
