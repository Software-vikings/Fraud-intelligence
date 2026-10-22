# FraudOps Intelligence

**A fraud operations portfolio application for transaction monitoring, alert investigation, case decisions and rule governance.**

FraudOps Intelligence is an independently built local demonstration of how a fintech fraud operations team could triage suspicious company-card payments, document analyst decisions, monitor rule behaviour and review portfolio-level indicators.

> **Data and claims boundary:** The project uses generated synthetic transactions and synthetic fraud labels only. It is not connected to Pleo or any payment provider. It does not demonstrate production deployment, real customer outcomes, or verified money saved / fraud prevented. All dashboard amounts and performance metrics are illustrative calculations on the generated dataset.

## What an organisation could use this workflow for

| Operational need | What the demonstration provides |
|---|---|
| Prioritise potentially suspicious payments | Alert queue sorted by risk score and amount |
| Understand why a transaction was flagged | Triggered rule, score contribution and human-readable reason |
| Record investigation outcomes | Case status, analyst assignment and mandatory investigation note |
| Preserve an audit trail | SQLite event history for every case action |
| Review detection behaviour | Precision, recall, false-positive rate and confusion counts |
| Inspect rule contribution | Retrospective rule trigger counts and synthetic-label overlap |
| Govern rule changes | Enable/disable and score changes with rationale and version history |

## Application screens

### Operations overview
Shows transaction volume, alert volume, precision, recall, false-positive rate, active investigation workload, decision distribution and transaction activity. It labels synthetic values explicitly and avoids presenting flagged transaction value as prevented loss.

### Alert queue and investigation workspace
Analysts can search and filter flagged transactions, inspect customer/merchant/transaction context, view triggered rules, assign a case, change its status and write an investigation note. Case actions are persisted in a local SQLite database with timestamped audit events.

Supported case statuses: OPEN, IN_REVIEW, ESCALATED, CONFIRMED_FRAUD, FALSE_POSITIVE and CLOSED.

### Rules and monitoring
Shows configured rules, retrospective trigger counts and overlap with synthetic labels. Users can enable/disable a rule or change its score. Every change requires a rationale and is written to the JSON-backed rule history.

## Run locally

Python 3.9 or newer is supported by the application code.

\`\`\`bash
git clone https://github.com/Software-vikings/Fraud-intelligence.git
cd Fraud-intelligence

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python scripts/generate_data.py
python scripts/run_evaluation.py
python -m pytest -v

uvicorn src.api.main:app --reload
\`\`\`

Open the analyst console at **http://127.0.0.1:8000/**.

The interactive API documentation remains available at **http://127.0.0.1:8000/docs** for developer testing; it is not the primary user interface.

### If the project is already on your Mac

\`\`\`bash
cd ~/Downloads/FraudOps-Intelligence/fraudops-intelligence
source .venv/bin/activate
python scripts/generate_data.py
python scripts/run_evaluation.py
python -m pytest -v
uvicorn src.api.main:app --reload
\`\`\`

If port 8000 is occupied, use another port:

\`\`\`bash
uvicorn src.api.main:app --reload --port 8001
\`\`\`

Then open http://127.0.0.1:8001/.

## API surface

| Endpoint | Purpose |
|---|---|
| GET / | Analyst web console |
| GET /health | Service and data health |
| GET /api/dashboard | Operations KPIs and decision distribution |
| GET /api/alerts | Filterable alert queue |
| GET /api/cases/{transaction_id} | Transaction context and case audit history |
| POST /api/cases/{transaction_id} | Record an analyst action |
| GET /api/rules/performance | Rule contribution summary |
| POST /api/rules/{rule_id} | Update rule enabled state / score with rationale |
| GET /rules | Raw rule configuration |
| GET /rule-history | Rule change history |
| POST /analyze | Score one submitted transaction |
| GET /evaluation | Dataset-level classification metrics |

## Evaluation interpretation

The dataset generator creates 3,000 labelled synthetic transactions. The baseline run recorded:

| Measure | Baseline result |
|---|---:|
| True positives | 95 |
| False positives | 80 |
| True negatives | 2,824 |
| False negatives | 1 |
| Precision | 54.29% |
| Recall | 98.96% |
| False-positive rate | 2.75% |
| Alerts | 175 |

These are reproducibility reference values for the current generated sample, not benchmark claims. A high recall with lower precision means the example catches most generated positive labels but also sends many non-fraud-labelled events to the alert queue. Rule thresholds need investigation and calibration.

The synthetic labels are created using patterns intentionally similar to the demonstration rules. This creates label/rule leakage and makes the current metrics optimistic as a measure of independent generalisation. They should not be used to claim real fraud model performance.

## Data and local persistence

- data/synthetic/transactions.csv: generated demonstration transactions.
- data/processed/transaction_decisions.csv: evaluated transaction decisions.
- data/processed/rule_metrics.csv: aggregate evaluation metrics.
- data/processed/fraudops_cases.sqlite: local case records and audit events, created when the API starts.
- data/rule_change_history.json: rule configuration change log.

Synthetic CSV data can be regenerated with python scripts/generate_data.py. Back up the SQLite database and rule history before deleting or replacing local data.

## Technical architecture

- **Python / FastAPI:** HTTP service, validation and API.
- **Python rule engine:** transparent, weighted rules and human-readable explanations.
- **Pandas / NumPy:** synthetic data generation and offline evaluation.
- **SQLite:** local case state and investigation event history.
- **HTML / CSS / JavaScript:** responsive analyst console, served by FastAPI.
- **pytest / FastAPI TestClient:** unit and API workflow tests.

## Important limitations before production

This is an employer-facing portfolio demonstration, not a production fraud platform.

1. No authentication, role-based permissions, multi-user concurrency controls or separation of duties.
2. SQLite and JSON files are local demonstration persistence, not a managed production data platform.
3. The generated dataset is synthetic, small and not representative of a real issuer/payment portfolio.
4. Synthetic label construction overlaps with rule indicators; a time-based holdout and independently generated labels are required for credible validation.
5. Velocity history in the offline evaluation is a simplified demonstration and is sensitive to event ordering. A production pipeline needs event-time ordering, late-arrival handling and robust rolling-window state.
6. Thresholds and scores are illustrative, not calibrated to a business loss function.
7. No deployment, alert streaming, external payment processor, customer/device graph, sanctions screening or model monitoring is included.
8. Human case decisions are demonstration actions and must not be interpreted as actual investigation outcomes.

Do not enter real payment-card data, personal information, credentials or confidential employer information. Do not expose this local demo to the public internet.

## Portfolio positioning

**FraudOps Intelligence — Independent Fraud Operations Portfolio Project**

Built a local fraud operations demonstration using Python, FastAPI, Pandas, SQLite and a browser-based analyst console. Implemented explainable transaction rules, risk-based alert triage, analyst case actions with audit history, rule-change governance and synthetic-data detection monitoring. Documented model/data limitations and evaluated precision, recall and false-positive behaviour.

Use this description only after you have personally run the latest version and can explain the design choices and limitations.
