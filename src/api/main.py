from pathlib import Path
import ast
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.engine.rules import evaluate_transaction
from src.engine.metrics import calculate_metrics
from src.governance.registry import RuleRegistry
from src.governance.case_store import CaseStore

BASE_DIR = Path(__file__).resolve().parents[2]
DATA = BASE_DIR / "data" / "synthetic" / "transactions.csv"
DECISIONS = BASE_DIR / "data" / "processed" / "transaction_decisions.csv"
CONFIG = BASE_DIR / "config" / "rules.json"
CASE_DB = BASE_DIR / "data" / "processed" / "fraudops_cases.sqlite"
STATIC = BASE_DIR / "static"

app = FastAPI(
    title="FraudOps Intelligence API",
    version="2.0.0",
    description="Local fraud operations portfolio demonstration using synthetic transactions.",
)
registry = RuleRegistry(config_path=CONFIG, history_path=BASE_DIR / "data" / "rule_change_history.json")
case_store = CaseStore(CASE_DB)


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    card_id: str
    amount: float = Field(ge=0)
    currency: str = "EUR"
    merchant_category: str
    merchant_id: str
    country: str
    home_country: str
    transaction_timestamp: str
    is_card_present: bool = False
    failed_attempts_24h: int = Field(default=0, ge=0)
    customer_avg_amount_30d: float = Field(default=50, ge=0)
    label_is_fraud: Optional[int] = None


class CaseAction(BaseModel):
    status: str
    assigned_to: str = "Demo Analyst"
    note: str = Field(min_length=5, max_length=1000)


class RuleAction(BaseModel):
    enabled: Optional[bool] = None
    score: Optional[int] = Field(default=None, ge=0, le=100)
    rationale: str = Field(min_length=5, max_length=500)
    changed_by: str = "Demo Analyst"


def _load_decisions():
    if not DECISIONS.exists():
        if not DATA.exists():
            return pd.DataFrame()
        raise HTTPException(404, "Decision dataset not generated. Run: python scripts/run_evaluation.py")
    return pd.read_csv(DECISIONS).fillna("")


def _alert_rows():
    frame = _load_decisions()
    if frame.empty or "decision" not in frame.columns:
        return []
    alerts = frame[frame["decision"].astype(str).str.upper() != "APPROVE"].copy()
    ids = alerts["transaction_id"].astype(str).tolist()
    case_store.ensure_cases(ids)
    cases = {item["transaction_id"]: item for item in case_store.list_cases()}
    records = alerts.to_dict(orient="records")
    for item in records:
        case = cases.get(str(item.get("transaction_id")), {})
        item["case_status"] = case.get("status", "OPEN")
        item["assigned_to"] = case.get("assigned_to", "Unassigned")
        item["latest_note"] = case.get("latest_note", "")
        item["case_updated_at"] = case.get("updated_at", "")
        item["risk_score"] = int(float(item.get("risk_score") or 0))
        item["amount"] = float(item.get("amount") or 0)
    records.sort(key=lambda row: (row["risk_score"], row["amount"]), reverse=True)
    return records


def _parse_hits(value):
    if isinstance(value, list):
        return value
    if not value:
        return []
    try:
        parsed = ast.literal_eval(str(value))
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError):
        return []


@app.get("/", include_in_schema=False)
def home():
    page = STATIC / "index.html"
    if not page.exists():
        raise HTTPException(404, "Web application files are missing.")
    return FileResponse(page)


@app.get("/health")
def health():
    return {"status": "ok", "project": "FraudOps Intelligence", "data_available": DATA.exists(),
            "decisions_available": DECISIONS.exists()}


@app.get("/rules")
def get_rules():
    return registry.get()


@app.get("/rule-history")
def rule_history():
    return registry.history()


@app.post("/analyze")
def analyze(tx: Transaction):
    rules_config = registry.get()
    result = evaluate_transaction(tx.model_dump(), rules=rules_config["rules"])
    thresholds = rules_config.get("decision_thresholds", {"review": 25, "decline": 60})
    score = result["risk_score"]
    result["decision"] = "DECLINE" if score >= thresholds["decline"] else "REVIEW" if score >= thresholds["review"] else "APPROVE"
    return result


@app.get("/transactions")
def transactions(limit: int = 100):
    if not DATA.exists():
        raise HTTPException(404, "Dataset not generated. Run: python scripts/generate_data.py")
    frame = pd.read_csv(DATA).head(max(1, min(limit, 1000)))
    return frame.fillna("").to_dict(orient="records")


@app.get("/evaluation")
def evaluation():
    rows = _load_decisions().to_dict(orient="records")
    return calculate_metrics(rows)


@app.get("/api/dashboard")
def dashboard():
    frame = _load_decisions()
    if frame.empty:
        raise HTTPException(404, "No evaluation data found. Run scripts/generate_data.py and scripts/run_evaluation.py.")
    rows = frame.to_dict(orient="records")
    metrics = calculate_metrics(rows)
    decisions = frame["decision"].astype(str).str.upper().value_counts().to_dict()
    flagged = frame[frame["decision"].astype(str).str.upper() != "APPROVE"]
    fraud = frame[frame["label_is_fraud"].astype(int) == 1] if "label_is_fraud" in frame else frame.iloc[0:0]
    alerts = _alert_rows()
    status_counts = {}
    for case in case_store.list_cases():
        status_counts[case["status"]] = status_counts.get(case["status"], 0) + 1
    daily = frame.copy()
    daily["day"] = pd.to_datetime(daily["transaction_timestamp"], errors="coerce").dt.strftime("%d %b")
    trend = daily.groupby("day", dropna=True).agg(transactions=("transaction_id", "count")).tail(10).reset_index().to_dict(orient="records")
    return {
        "metrics": metrics,
        "decision_counts": {key: int(value) for key, value in decisions.items()},
        "case_status_counts": status_counts,
        "alert_count": len(alerts),
        "flagged_value": round(float(flagged["amount"].astype(float).sum()), 2),
        "synthetic_fraud_value": round(float(fraud["amount"].astype(float).sum()), 2),
        "open_cases": sum(1 for item in case_store.list_cases() if item["status"] in {"OPEN", "IN_REVIEW", "ESCALATED"}),
        "trend": trend,
        "data_notice": "Synthetic labelled data. Flagged value is transaction volume under review, not confirmed loss or proven fraud prevented.",
    }


@app.get("/api/alerts")
def alerts(status: Optional[str] = None, decision: Optional[str] = None, search: Optional[str] = None):
    rows = _alert_rows()
    if status and status.upper() != "ALL":
        rows = [row for row in rows if row["case_status"] == status.upper()]
    if decision and decision.upper() != "ALL":
        rows = [row for row in rows if str(row["decision"]).upper() == decision.upper()]
    if search:
        query = search.lower()
        rows = [row for row in rows if query in " ".join(str(row.get(key, "")) for key in
                 ("transaction_id", "customer_id", "merchant_id", "merchant_category", "country")).lower()]
    return {"total": len(rows), "items": rows[:500]}


@app.get("/api/cases/{transaction_id}")
def get_case(transaction_id: str):
    match = next((row for row in _alert_rows() if str(row.get("transaction_id")) == transaction_id), None)
    if not match:
        raise HTTPException(404, "Alert not found.")
    match["triggered_rules"] = _parse_hits(match.get("triggered_rules"))
    match["history"] = case_store.history(transaction_id)
    return match


@app.post("/api/cases/{transaction_id}")
def update_case(transaction_id: str, action: CaseAction):
    known = any(str(row.get("transaction_id")) == transaction_id for row in _alert_rows())
    if not known:
        raise HTTPException(404, "Alert not found.")
    try:
        case = case_store.update_case(transaction_id, action.status, action.assigned_to, action.note)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"case": case, "history": case_store.history(transaction_id)}


@app.get("/api/rules/performance")
def rules_performance():
    frame = _load_decisions()
    rules_config = registry.get()
    summary = {}
    if not frame.empty:
        for _, row in frame.iterrows():
            fraud_label = int(row.get("label_is_fraud", 0) or 0)
            for hit in _parse_hits(row.get("triggered_rules")):
                rid = hit.get("rule_id")
                entry = summary.setdefault(rid, {"rule_id": rid, "name": hit.get("rule_name", rid),
                                                  "triggers": 0, "fraud_label_hits": 0,
                                                  "non_fraud_triggers": 0, "score": 0})
                entry["triggers"] += 1
                entry["fraud_label_hits"] += int(fraud_label == 1)
                entry["non_fraud_triggers"] += int(fraud_label == 0)
                entry["score"] = int(hit.get("score", 0))
    configured = {rule["id"]: rule for rule in rules_config.get("rules", [])}
    output = []
    for rid, config in configured.items():
        item = summary.get(rid, {"rule_id": rid, "name": config["name"], "triggers": 0,
                                 "fraud_label_hits": 0, "non_fraud_triggers": 0, "score": config.get("score", 0)})
        item.update({"enabled": config.get("enabled", True), "configured_score": config.get("score", 0)})
        output.append(item)
    return {"items": output, "notice": "Rule hit counts are retrospective on this synthetic dataset; they are not causal estimates of prevented fraud."}


@app.post("/api/rules/{rule_id}")
def update_rule(rule_id: str, action: RuleAction):
    updates = {}
    if action.enabled is not None:
        updates["enabled"] = action.enabled
    if action.score is not None:
        updates["score"] = action.score
    if not updates:
        raise HTTPException(422, "Provide enabled and/or score to update.")
    try:
        updated = registry.update_rule(rule_id, updates, action.changed_by, action.rationale)
    except KeyError:
        raise HTTPException(404, "Rule not found.")
    return {"updated_rule": updated, "history": registry.history()}
