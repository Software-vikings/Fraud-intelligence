# Demonstration Rule Catalogue

| ID | Rule | Trigger | Default points |
|---|---|---|---:|
| R001 | Unusually high amount | Amount ≥ 8× customer's 30-day average | 35 |
| R002 | Card velocity | More than 4 transactions in 10 minutes | 30 |
| R003 | Country mismatch | Transaction country differs from home country | 20 |
| R004 | Repeated failed attempts | At least 3 failed attempts in prior 24 hours | 20 |
| R005 | High-risk merchant category | Category is crypto, cash equivalent or gambling | 15 |

These are illustrative hypotheses for synthetic data, not recommended production thresholds. Thresholds must be validated against the institution's customers, products, fraud losses and customer-friction costs.
