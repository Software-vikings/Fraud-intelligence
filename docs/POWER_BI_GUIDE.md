# Power BI Dashboard Guide

Run `python scripts/run_evaluation.py` first. Import:
- `data/processed/transaction_decisions.csv`
- `data/processed/rule_metrics.csv`

Suggested report pages:
1. **Executive overview:** transaction count, alert count, precision, recall and false-positive rate.
2. **Fraud trends:** labelled fraud by date, amount band and merchant category.
3. **Rule performance:** triggered count by rule ID, severity and decision outcome.
4. **Customer friction:** review/decline volume and false-positive share.

Suggested DAX measures (adjust table names after import):

```DAX
Transaction Count = COUNTROWS(transaction_decisions)
Alert Count =
CALCULATE(COUNTROWS(transaction_decisions),
    transaction_decisions[decision] IN {"REVIEW", "DECLINE"})
Labelled Fraud =
CALCULATE(COUNTROWS(transaction_decisions),
    transaction_decisions[label_is_fraud] = 1)
False Positives =
CALCULATE(COUNTROWS(transaction_decisions),
    transaction_decisions[label_is_fraud] = 0,
    transaction_decisions[decision] IN {"REVIEW", "DECLINE"})
```

Use clear labels stating that the dataset is synthetic and the results are illustrative.
