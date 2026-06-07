def compute_binary_metrics(
    true_labels: list[int],
    predicted_labels: list[int],
) -> dict:
    if len(true_labels) != len(predicted_labels):
        raise ValueError("true_labels and predicted_labels must have the same length")
    if not true_labels:
        raise ValueError("at least one label is required")

    tn = fp = fn = tp = 0
    for actual, predicted in zip(true_labels, predicted_labels):
        if actual not in (0, 1) or predicted not in (0, 1):
            raise ValueError("binary metrics require labels 0 or 1")
        if actual == 0 and predicted == 0:
            tn += 1
        elif actual == 0 and predicted == 1:
            fp += 1
        elif actual == 1 and predicted == 0:
            fn += 1
        else:
            tp += 1

    total = tn + fp + fn + tp
    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": [[tn, fp], [fn, tp]],
        "support": {"outside": tn + fp, "inside": fn + tp},
    }
