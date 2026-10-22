from pathlib import Path
import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from src.engine.rules import evaluate_transaction
from src.engine.metrics import calculate_metrics
from src.governance.registry import RuleRegistry

app = FastAPI(title="FraudOps Intelligence API", version="1.0.0",
              description="Synthetic-data portfolio demonstration for fraud rules and decisioning.")
DATA = Path("data/synthetic/transactions.csv")
registry = RuleRegistry()

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

@app.get("/health")
def health():
    return {"status":"ok","project":"FraudOps Intelligence","data_available":DATA.exists()}

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
    thresholds = rules_config.get("decision_thresholds", {"review":25,"decline":60})
    score = result["risk_score"]
    result["decision"] = "DECLINE" if score >= thresholds["decline"] else "REVIEW" if score >= thresholds["review"] else "APPROVE"
    return result

@app.get("/transactions")
def transactions(limit: int = 100):
    if not DATA.exists():
        raise HTTPException(404, "Dataset not generated. Run: python scripts/generate_data.py")
    df = pd.read_csv(DATA).head(max(1,min(limit,1000)))
    return df.fillna("").to_dict(orient="records")

@app.get("/evaluation")
def evaluation():
    path = Path("data/processed/transaction_decisions.csv")
    if not path.exists():
        raise HTTPException(404, "Run python scripts/run_evaluation.py first.")
    rows = pd.read_csv(path).fillna("").to_dict(orient="records")
    return calculate_metrics(rows)
