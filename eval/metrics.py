"""
Automated Evaluation Metrics for Intent Classification and Escalation Decision.
Computes Accuracy, Precision, Recall, Macro-F1, and Confusion Matrices.
"""

from typing import List, Dict, Any
from collections import defaultdict

class EvaluationMetrics:
    @staticmethod
    def compute_classification_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
        """
        Computes multiclass precision, recall, macro-F1, and overall accuracy.
        """
        assert len(y_true) == len(y_pred), "Mismatched length between y_true and y_pred"
        total = len(y_true)
        if total == 0:
            return {}

        classes = sorted(list(set(y_true + y_pred)))
        class_stats = {}

        tp = defaultdict(int)
        fp = defaultdict(int)
        fn = defaultdict(int)

        correct = 0
        for yt, yp in zip(y_true, y_pred):
            if yt == yp:
                correct += 1
                tp[yt] += 1
            else:
                fp[yp] += 1
                fn[yt] += 1

        accuracy = correct / total

        precisions = []
        recalls = []
        f1s = []

        for c in classes:
            c_tp = tp[c]
            c_fp = fp[c]
            c_fn = fn[c]

            prec = c_tp / (c_tp + c_fp) if (c_tp + c_fp) > 0 else 0.0
            rec = c_tp / (c_tp + c_fn) if (c_tp + c_fn) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

            class_stats[c] = {
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "support": c_tp + c_fn
            }
            precisions.append(prec)
            recalls.append(rec)
            f1s.append(f1)

        macro_prec = sum(precisions) / len(classes) if classes else 0.0
        macro_rec = sum(recalls) / len(classes) if classes else 0.0
        macro_f1 = sum(f1s) / len(classes) if classes else 0.0

        return {
            "accuracy": round(accuracy, 4),
            "macro_precision": round(macro_prec, 4),
            "macro_recall": round(macro_rec, 4),
            "macro_f1": round(macro_f1, 4),
            "per_class": class_stats,
            "total_samples": total
        }

    @staticmethod
    def compute_escalation_metrics(y_true: List[bool], y_pred: List[bool]) -> Dict[str, Any]:
        """
        Computes binary metrics specifically for the Escalation Decision (True = ESCALATE).
        Crucial: Escalation Recall (missed escalations) vs Escalation Precision (wasted agent time).
        """
        assert len(y_true) == len(y_pred)
        total = len(y_true)

        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt is True and yp is True)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt is False and yp is True)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt is True and yp is False)
        tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt is False and yp is False)

        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": {
                "true_escalate_pred_escalate (TP)": tp,
                "true_autohandle_pred_escalate (FP)": fp,
                "true_escalate_pred_autohandle (FN) - DANGEROUS": fn,
                "true_autohandle_pred_autohandle (TN)": tn
            },
            "missed_escalation_rate (FN Rate)": round(fn / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        }
