"""
Unit Tests for @AppleSupport AI Agent Pipeline.
"""

import unittest
from src.preprocessor import TweetPreprocessor
from src.classifier import IntentClassifier
from src.escalation import EscalationEngine
from src.retriever import HistoricalRetriever
from src.agent import AppleSupportAgent
from eval.metrics import EvaluationMetrics

class TestAppleSupportAgent(unittest.TestCase):
    def setUp(self):
        self.agent = AppleSupportAgent()
        self.preprocessor = TweetPreprocessor()
        self.classifier = IntentClassifier()
        self.escalator = EscalationEngine()
        self.retriever = HistoricalRetriever()

    def test_preprocessor_handle_stripping(self):
        raw = "@AppleSupport @tim_cook my phone is broken!! https://apple.com"
        cleaned = self.preprocessor.clean_text(raw)
        self.assertNotIn("@AppleSupport", cleaned)
        self.assertNotIn("https://", cleaned)
        self.assertIn("phone is broken", cleaned)

    def test_preprocessor_shouting_and_distress(self):
        raw = "HELP MY IPHONE IS EXPLODING RIGHT NOW!!!!"
        features = self.preprocessor.extract_features(raw)
        self.assertTrue(features["is_shouting"])
        self.assertTrue(features["has_emergency_keyword"])
        self.assertTrue(features["has_distress_punct"])

    def test_intent_classifier_battery(self):
        res = self.classifier.predict("My battery health dropped from 100% to 80% very fast.")
        self.assertEqual(res["top_intent"], "DEVICE_BATTERY_POWER")
        self.assertGreater(res["confidence"], 0.3)

    def test_intent_classifier_billing(self):
        res = self.classifier.predict("Apple charged my card $14.99 for a subscription I did not buy.")
        self.assertEqual(res["top_intent"], "SUBSCRIPTION_BILLING")

    def test_safety_hazard_escalation(self):
        raw = "URGENT: My battery is swollen and smoking on the charger!"
        res = self.agent.process(raw)
        self.assertTrue(res["should_escalate"])
        self.assertEqual(res["decision"], "ESCALATE")
        self.assertEqual(res["risk_category"], "SAFETY_HAZARD")
        self.assertIn("Safety/Hazard Flag", res["stated_reason"])

    def test_hardware_damage_escalation(self):
        raw = "Dropped phone on concrete and front screen glass is shattered."
        res = self.agent.process(raw)
        self.assertTrue(res["should_escalate"])
        self.assertIn("support.apple.com/repair", res["draft_reply"])

    def test_standard_autohandle_query(self):
        raw = "Where do I find my active subscriptions to cancel one?"
        res = self.agent.process(raw)
        self.assertFalse(res["should_escalate"])
        self.assertEqual(res["decision"], "AUTO_HANDLE")
        self.assertIn("reportaproblem.apple.com", res["draft_reply"])

    def test_metrics_computation(self):
        y_true = ["A", "B", "A"]
        y_pred = ["A", "B", "B"]
        metrics = EvaluationMetrics.compute_classification_metrics(y_true, y_pred)
        self.assertAlmostEqual(metrics["accuracy"], 2/3, places=2)

if __name__ == "__main__":
    unittest.main()
