"""
Baseline 2: Simple Uncalibrated TF-IDF Baseline.
- Intent: Uncalibrated Bag-of-Words similarity without domain weighting.
- Escalation: Coarse intent-level rule (only escalates HARDWARE_PHYSICAL_DAMAGE and APPLE_ID_SECURITY).
- Reply: Basic generic response per intent without historical RAG grounding or official KB links.
"""

import re
import math
from typing import Dict, Any, List

class SimpleBaselineAgent:
    def __init__(self):
        self.intents = [
            "DEVICE_BATTERY_POWER",
            "OS_SOFTWARE_UPDATE",
            "APPLE_ID_SECURITY",
            "HARDWARE_PHYSICAL_DAMAGE",
            "SUBSCRIPTION_BILLING",
            "CONNECTIVITY_ACCESSORIES"
        ]
        self.intent_words = {
            "DEVICE_BATTERY_POWER": ["battery", "drain", "charge", "hot", "power"],
            "OS_SOFTWARE_UPDATE": ["update", "ios", "freeze", "crash", "bug", "lag"],
            "APPLE_ID_SECURITY": ["apple id", "password", "locked", "icloud", "hacked", "security"],
            "HARDWARE_PHYSICAL_DAMAGE": ["screen", "cracked", "damage", "broken", "liquid", "dropped"],
            "SUBSCRIPTION_BILLING": ["refund", "charged", "billing", "subscription", "money", "receipt"],
            "CONNECTIVITY_ACCESSORIES": ["wifi", "bluetooth", "airpods", "carplay", "watch", "pairing"]
        }

    def process(self, raw_tweet: str) -> Dict[str, Any]:
        lower = raw_tweet.lower()
        scores = {}
        for intent, words in self.intent_words.items():
            count = sum(1 for w in words if w in lower)
            scores[intent] = count

        best_intent = max(scores, key=scores.get)
        confidence = 0.50 if scores[best_intent] > 0 else 0.16

        # Coarse intent-only escalation (blind to fire, legal, specific billing disputes)
        should_escalate = best_intent in ["HARDWARE_PHYSICAL_DAMAGE", "APPLE_ID_SECURITY"]
        decision = "ESCALATE" if should_escalate else "AUTO_HANDLE"
        stated_reason = f"Simple rule: Category {best_intent} is marked as escalate" if should_escalate else "Simple rule: Category is auto-handled"

        draft_reply = f"Hello, we see you are having trouble with your {best_intent.replace('_', ' ').title()}. Please check the Apple website or visit an Apple Store."

        return {
            "query": raw_tweet,
            "predicted_intent": best_intent,
            "intent_confidence": confidence,
            "decision": decision,
            "should_escalate": should_escalate,
            "stated_reason": stated_reason,
            "draft_reply": draft_reply
        }
