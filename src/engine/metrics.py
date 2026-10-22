from __future__ import annotations
from typing import Iterable

def calculate_metrics(rows: Iterable[dict]) -> dict:
    """Treat REVIEW or DECLINE as an alert; compare with synthetic fraud labels."""
    tp = fp = tn = fn = 0
    for row in rows:
        actual = int(row.get("label_is_fraud", 0)) == 1
        predicted = row.get("decision") in {"REVIEW", "DECLINE"}
        if actual and predicted: tp += 1
        elif not actual and predicted: fp += 1
        elif actual and not predicted: fn += 1
        else: tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {"true_positives":tp,"false_positives":fp,"true_negatives":tn,"false_negatives":fn,
            "precision":round(precision,4),"recall":round(recall,4),
            "false_positive_rate":round(fpr,4),"alert_count":tp+fp,"transaction_count":tp+fp+tn+fn}
