"""
Statistical Inter-Annotator & Human-Judge Agreement Engine.
Calculates:
1. Cohen's Kappa (κ) for categorical agreement (High / Medium / Low quality)
2. Pearson Correlation Coefficient (r) for continuous rating alignment
3. Mean Absolute Error (MAE)
"""

import math
from typing import List, Dict, Any

class HumanJudgeAgreement:
    @staticmethod
    def _categorize(score: float) -> str:
        """Bins continuous 1.0-5.0 score into 3 ordinal quality tiers."""
        if score >= 4.0:
            return "HIGH"
        elif score >= 2.5:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def compute_cohens_kappa(human_scores: List[float], judge_scores: List[float]) -> Dict[str, Any]:
        """
        Calculates Cohen's Kappa coefficient (κ) between human ratings and LLM judge ratings.
        κ = (Po - Pe) / (1 - Pe)
        """
        assert len(human_scores) == len(judge_scores), "Scores list length mismatch"
        n = len(human_scores)
        if n == 0:
            return {}

        human_cats = [HumanJudgeAgreement._categorize(s) for s in human_scores]
        judge_cats = [HumanJudgeAgreement._categorize(s) for s in judge_scores]

        categories = ["HIGH", "MEDIUM", "LOW"]
        matrix = {c1: {c2: 0 for c2 in categories} for c1 in categories}

        for h, j in zip(human_cats, judge_cats):
            matrix[h][j] += 1

        # Observed agreement (Po)
        observed_agreements = sum(matrix[c][c] for c in categories)
        po = observed_agreements / n

        # Expected agreement by chance (Pe)
        pe = 0.0
        for c in categories:
            human_marginal = sum(matrix[c][j] for j in categories) / n
            judge_marginal = sum(matrix[h][c] for h in categories) / n
            pe += human_marginal * judge_marginal

        kappa = (po - pe) / (1.0 - pe) if (1.0 - pe) > 0 else 1.0

        # Landis & Koch (1977) benchmark interpretation
        if kappa > 0.80:
            interpretation = "Almost Perfect Agreement (κ > 0.80)"
        elif kappa > 0.60:
            interpretation = "Substantial Agreement (0.61 - 0.80)"
        elif kappa > 0.40:
            interpretation = "Moderate Agreement (0.41 - 0.60)"
        elif kappa > 0.20:
            interpretation = "Fair Agreement (0.21 - 0.40)"
        else:
            interpretation = "Slight / Poor Agreement (κ <= 0.20)"

        return {
            "cohens_kappa": round(kappa, 4),
            "observed_agreement_po": round(po, 4),
            "chance_agreement_pe": round(pe, 4),
            "interpretation": interpretation,
            "confusion_matrix": matrix
        }

    @staticmethod
    def compute_pearson_correlation(human_scores: List[float], judge_scores: List[float]) -> Dict[str, Any]:
        """Calculates Pearson correlation coefficient r and MAE."""
        n = len(human_scores)
        mean_h = sum(human_scores) / n
        mean_j = sum(judge_scores) / n

        numerator = sum((h - mean_h) * (j - mean_j) for h, j in zip(human_scores, judge_scores))
        denom_h = math.sqrt(sum((h - mean_h) ** 2 for h in human_scores))
        denom_j = math.sqrt(sum((j - mean_j) ** 2 for j in judge_scores))

        r = numerator / (denom_h * denom_j) if (denom_h * denom_j) > 0 else 0.0
        mae = sum(abs(h - j) for h, j in zip(human_scores, judge_scores)) / n

        return {
            "pearson_r": round(r, 4),
            "mean_absolute_error": round(mae, 4)
        }
