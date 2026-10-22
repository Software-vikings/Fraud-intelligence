from src.engine.metrics import calculate_metrics

def test_metrics_confusion_matrix():
    rows = [
        {"label_is_fraud":1,"decision":"REVIEW"},
        {"label_is_fraud":0,"decision":"DECLINE"},
        {"label_is_fraud":0,"decision":"APPROVE"},
        {"label_is_fraud":1,"decision":"APPROVE"},
    ]
    m = calculate_metrics(rows)
    assert (m["true_positives"],m["false_positives"],m["true_negatives"],m["false_negatives"]) == (1,1,1,1)
    assert m["precision"] == 0.5
    assert m["recall"] == 0.5
