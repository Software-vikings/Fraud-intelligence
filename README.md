# FraudOps Intelligence
**Independent fintech fraud decisioning and monitoring portfolio project**

FraudOps Intelligence is a runnable demonstration platform for analysing synthetic payment transactions, applying configurable fraud rules, producing explainable risk decisions, evaluating detection performance, and tracking rule changes.

> **Important:** This is an independent portfolio demonstration using synthetic data. It is not a production fraud system, does not process real payment data, and does not claim employment or deployment experience at any financial institution.

## What it demonstrates
- SQL data model and analytical queries for transaction monitoring.
- Python rule engine with configurable thresholds and explainable alerts.
- Decision outcomes: `APPROVE`, `REVIEW`, and `DECLINE`.
- Evaluation against synthetic labelled data: precision, recall, false-positive rate and confusion counts.
- Rule configuration and versioned change history (JSON-backed demo store).
- FastAPI endpoints and automated tests.
- GitHub Actions CI workflow.
- Optional Power BI dashboard using exported CSV files.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py
uvicorn src.api.main:app --reload
```

Open:
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health
- Run analysis: `POST /analyze`
- List transactions: `GET /transactions`

Run tests:
```bash
pytest -q
```

Run the command-line evaluation:
```bash
python scripts/run_evaluation.py
```

## Example API request

```json
{
  "transaction_id": "TX000001",
  "customer_id": "C001",
  "card_id": "CARD001",
  "amount": 2450.0,
  "currency": "EUR",
  "merchant_category": "electronics",
  "merchant_id": "M009",
  "country": "ES",
  "home_country": "ES",
  "transaction_timestamp": "2026-01-12T11:30:00",
  "is_card_present": false,
  "failed_attempts_24h": 0,
  "customer_avg_amount_30d": 85.0,
  "label_is_fraud": 0
}
```

## Repository map

```text
src/
  api/             FastAPI application and request/response schemas
  engine/           Rule evaluation, decisions and metrics
  governance/       Rule registry and change history
  data/             Dataset loading utilities
config/             Rule configuration
database/           SQL schema and analytical queries
data/                Generated synthetic data and dictionary
scripts/             Data generation and evaluation commands
tests/               Unit and API tests
powerbi/             Dashboard build guide and measures
docs/                Architecture, rules, limitations and test strategy
.github/workflows/   Continuous integration
```

## Rule catalogue
The default rule set is in `config/rules.json`. Rules are intentionally transparent:
1. High transaction amount compared with the customer's historical average.
2. High transaction velocity for a card within a rolling 10-minute window.
3. Transaction in a country different from the customer's home country.
4. Multiple failed attempts in the previous 24 hours.
5. High-risk merchant category.

Each rule emits a reason, severity and score contribution. The final decision is based on the combined score and configurable decision thresholds.

## Evaluation and limitations
The generated dataset includes synthetic fraud labels. Metrics are calculated against those labels only to demonstrate an evaluation workflow. Results are not evidence of real-world model performance. The rule engine uses simplified example logic; production systems require calibrated thresholds, robust identity/device context, privacy controls, human review, monitoring, governance, and institution-specific validation.

## Power BI
See [`powerbi/POWER_BI_GUIDE.md`](powerbi/POWER_BI_GUIDE.md). The evaluation script exports `data/processed/transaction_decisions.csv` and `data/processed/rule_metrics.csv`, which can be imported into Power BI.

## Suggested CV wording
**FraudOps Intelligence — Independent Portfolio Project**
Built a Python-based transaction monitoring and fraud decisioning demonstration using synthetic payment data. Implemented configurable fraud rules, explainable approve/review/decline outcomes, SQL analytics, evaluation metrics, automated tests and CI workflow. Evaluated rule behaviour using precision, recall and false-positive analysis.

Only use this wording after running the project and being able to explain its design and limitations.
