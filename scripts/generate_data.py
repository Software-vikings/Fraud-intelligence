from pathlib import Path
from datetime import timedelta
import numpy as np
import pandas as pd

def main(n=3000, seed=42):
    rng = np.random.default_rng(seed)
    customers = [f"C{i:04d}" for i in range(1,151)]
    countries = ["ES","FR","DE","NL","IT","PT"]
    categories = ["groceries","travel","software","office","electronics","restaurants","crypto","cash_equivalent","gambling"]
    rows = []
    base_time = pd.Timestamp("2026-01-01T00:00:00")
    for i in range(n):
        customer = rng.choice(customers)
        home = rng.choice(countries)
        fraud = int(rng.random() < 0.035)
        avg = float(rng.lognormal(3.5,0.55))
        amount = float(rng.lognormal(3.7,0.8))
        country = home
        category = rng.choice(categories[:6])
        failed = int(rng.poisson(0.25))
        if fraud:
            amount *= float(rng.uniform(8,18))
            country = rng.choice([c for c in countries if c != home])
            category = rng.choice(["electronics","crypto","cash_equivalent","gambling"])
            failed = int(rng.integers(2,6))
        ts = base_time + timedelta(minutes=int(rng.integers(0, 60 * 24 * 60)))
        rows.append({
            "transaction_id":f"TX{i+1:06d}","customer_id":customer,"card_id":f"CARD{int(customer[1:]):04d}",
            "amount":round(amount,2),"currency":"EUR","merchant_category":category,
            "merchant_id":f"M{int(rng.integers(1,180)):04d}","country":country,"home_country":home,
            "transaction_timestamp":ts.isoformat(),"is_card_present":bool(rng.integers(0,2)),
            "failed_attempts_24h":failed,"customer_avg_amount_30d":round(avg,2),"label_is_fraud":fraud
        })
    df = pd.DataFrame(rows)
    path = Path("data/synthetic/transactions.csv")
    path.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(path,index=False)
    print(f"Generated {len(df)} synthetic transactions at {path}")
if __name__ == "__main__":
    main()
