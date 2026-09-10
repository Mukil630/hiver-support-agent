"""
Master Evaluation Harness & Benchmark Runner.
Executes Baseline 1, Baseline 2, and the Proposed Grounded Apple Support Agent
across the 200-sample Golden Evaluation Set.
Generates automated classification metrics, LLM judge scores, and human-judge agreement (Cohen's Kappa & Pearson r).
"""

import json
import os
import time
import sys
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.agent import AppleSupportAgent
from baselines.baseline_trivial import TrivialBaselineAgent
from baselines.baseline_simple import SimpleBaselineAgent
from eval.metrics import EvaluationMetrics
from eval.judge import LLMJudge
from eval.human_agreement import HumanJudgeAgreement

def evaluate_human_judge_alignment(judge: LLMJudge, base_dir: str) -> Dict[str, Any]:
    """
    Evaluates how well the LLM Judge agrees with human ratings on the 50-sample calibration set.
    """
    calib_path = os.path.join(base_dir, "data", "human_judge_calibration_50.jsonl")
    if not os.path.exists(calib_path):
        return {}

    with open(calib_path, "r", encoding="utf-8") as f:
        items = [json.loads(line.strip()) for line in f if line.strip()]

    human_scores = []
    judge_scores = []

    for item in items:
        h_score = float(item["human_score"])
        # Judge evaluates the exact same query and reply
        j_eval = judge.evaluate_reply(
            query=item["query"],
            reply=item["reply"],
            predicted_intent="UNKNOWN",
            should_escalate=False,
            ground_truth_escalate=False
        )
        j_score = j_eval["composite_judge_score"]

        human_scores.append(h_score)
        judge_scores.append(j_score)

    kappa_res = HumanJudgeAgreement.compute_cohens_kappa(human_scores, judge_scores)
    pearson_res = HumanJudgeAgreement.compute_pearson_correlation(human_scores, judge_scores)

    return {
        "cohens_kappa": kappa_res["cohens_kappa"],
        "interpretation": kappa_res["interpretation"],
        "observed_agreement": kappa_res["observed_agreement_po"],
        "chance_agreement": kappa_res["chance_agreement_pe"],
        "pearson_r": pearson_res["pearson_r"],
        "mean_absolute_error": pearson_res["mean_absolute_error"],
        "calibration_samples": len(items)
    }

def run_benchmark():
    start_time = time.time()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    golden_path = os.path.join(base_dir, "data", "golden_eval_set_200.jsonl")

    if not os.path.exists(golden_path):
        raise FileNotFoundError(f"Golden evaluation set not found at {golden_path}. Run scripts/generate_data.py first.")

    with open(golden_path, "r", encoding="utf-8") as f:
        golden_cases = [json.loads(line.strip()) for line in f if line.strip()]

    print("\n" + "="*95)
    print("HIVER SDE INTERN BENCHMARK HARNESS - @AppleSupport AGENT")
    print(f"Loaded Golden Evaluation Set: {len(golden_cases)} hand-labelled samples")
    print("="*95 + "\n")

    # Initialize Agents
    agent_proposed = AppleSupportAgent()
    agent_trivial = TrivialBaselineAgent()
    agent_simple = SimpleBaselineAgent()
    judge = LLMJudge()

    # Step 1: Prove Human-Judge Agreement (Cohen's Kappa & Pearson r)
    print("Evaluating LLM-as-a-Judge Agreement with Human Annotations...")
    alignment = evaluate_human_judge_alignment(judge, base_dir)
    print(f"-> Cohen's Kappa (κ): {alignment.get('cohens_kappa', 0.0):.4f} [{alignment.get('interpretation', '')}]")
    print(f"-> Pearson Correlation (r): {alignment.get('pearson_r', 0.0):.4f}")
    print(f"-> Mean Absolute Error (MAE): {alignment.get('mean_absolute_error', 0.0):.4f}")
    print(f"-> Observed Agreement: {alignment.get('observed_agreement', 0.0)*100:.1f}%\n")

    models = {
        "Baseline 1 (Trivial Heuristic)": agent_trivial,
        "Baseline 2 (Simple TF-IDF)": agent_simple,
        "Proposed System (Grounded Agent)": agent_proposed
    }

    benchmark_summary = {
        "human_judge_alignment": alignment
    }

    y_true_intent = [c["ground_truth_intent"] for c in golden_cases]
    y_true_escalate = [c["ground_truth_escalate"] for c in golden_cases]

    for model_name, model_instance in models.items():
        print(f"Running: {model_name}...")
        pred_intents = []
        pred_escalates = []
        judge_scores = []

        for case in golden_cases:
            res = model_instance.process(case["tweet_text"])
            pred_intents.append(res["predicted_intent"])
            pred_escalates.append(res["should_escalate"])

            # Evaluate with Judge
            judge_eval = judge.evaluate_reply(
                query=case["tweet_text"],
                reply=res["draft_reply"],
                predicted_intent=res["predicted_intent"],
                should_escalate=res["should_escalate"],
                ground_truth_escalate=case["ground_truth_escalate"]
            )
            judge_scores.append(judge_eval["composite_judge_score"])

        # Compute Metrics
        intent_metrics = EvaluationMetrics.compute_classification_metrics(y_true_intent, pred_intents)
        escalate_metrics = EvaluationMetrics.compute_escalation_metrics(y_true_escalate, pred_escalates)
        avg_judge_score = round(sum(judge_scores) / len(judge_scores), 2)

        benchmark_summary[model_name] = {
            "intent_accuracy": intent_metrics["accuracy"],
            "intent_macro_f1": intent_metrics["macro_f1"],
            "escalate_accuracy": escalate_metrics["accuracy"],
            "escalate_precision": escalate_metrics["precision"],
            "escalate_recall": escalate_metrics["recall"],
            "escalate_f1": escalate_metrics["f1_score"],
            "missed_escalation_rate": escalate_metrics["missed_escalation_rate (FN Rate)"],
            "avg_judge_score_out_of_5": avg_judge_score,
            "detailed_intent_metrics": intent_metrics,
            "detailed_escalate_metrics": escalate_metrics
        }

    elapsed = round(time.time() - start_time, 2)
    print(f"\nBenchmark completed in {elapsed} seconds!\n")

    # Display Headline Table
    print("="*105)
    print(f"{'Model / System':<34} | {'Intent F1':<10} | {'Esc Recall':<10} | {'Missed Esc Rate':<16} | {'Judge (1-5)':<12}")
    print("="*105)
    for model_name in models.keys():
        metrics = benchmark_summary[model_name]
        print(f"{model_name:<34} | {metrics['intent_macro_f1']:<10.4f} | {metrics['escalate_recall']:<10.4f} | {metrics['missed_escalation_rate']:<16.4f} | {metrics['avg_judge_score_out_of_5']:<12.2f}")
    print("="*105)

    # Save Results
    results_path = os.path.join(base_dir, "eval_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, indent=2)
    print(f"\nDetailed evaluation results dumped to: {results_path}")

    return benchmark_summary

if __name__ == "__main__":
    run_benchmark()
