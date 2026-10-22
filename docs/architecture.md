# Architecture

## Flow
Synthetic transaction CSV / API request → validation → fraud rule evaluation → risk score → decision → evaluation and monitoring exports.

## Components
- **Data layer:** synthetic labelled transaction dataset and SQL schema.
- **Rule engine:** deterministic, configurable rules with per-rule explanations.
- **Decision layer:** maps aggregate score to approve, review or decline.
- **Governance layer:** JSON-backed local rule configuration and change history.
- **API:** FastAPI endpoints for health, rules, transactions, analysis and evaluation.
- **Quality:** Pytest unit/API tests and GitHub Actions CI.

## Design choices
The first implementation is deliberately rules-first. Transparent rules make it possible to explain why a transaction was flagged and to measure the operational consequences of changing a threshold. Machine learning can be added later as a challenger model, not as an unexplained replacement for controls.
