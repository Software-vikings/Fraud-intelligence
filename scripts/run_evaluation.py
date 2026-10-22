from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from src.engine.rules import evaluate_transaction, DEFAULT_RULES
from src.engine.metrics import calculate_metrics

def main():
    source = Path("data/synthetic/transactions.csv")
    if not source.exists():
        raise SystemExit("Dataset missing. Run python scripts/generate_data.py")
    df = pd.read_csv(source)
    rows = df.to_dict(orient="records")
    decisions = []
    history = []
    for row in rows:
        result = evaluate_transaction(row, history=history, rules=DEFAULT_RULES)
        decisions.append({**row, **result})
        history.append(row)
    out = Path("data/processed")
    out.mkdir(parents=True,exist_ok=True)
    result_df = pd.DataFrame(decisions)
    result_df.to_csv(out/"transaction_decisions.csv",index=False)
    metrics = calculate_metrics(decisions)
    pd.DataFrame([metrics]).to_csv(out/"rule_metrics.csv",index=False)
    print("Evaluation metrics (synthetic labelled data):")
    for k,v in metrics.items(): print(f"{k}: {v}")
    print(f"Exports saved in {out}")
if __name__ == "__main__":
    main()
