"""
Baseline 1: Trivial Heuristic Baseline.
- Intent: Predicts majority class ('DEVICE_BATTERY_POWER').
- Escalation: 2-keyword regex check ('refund', 'broken').
- Reply: Fixed static canned apology template without grounding.
"""

from typing import Dict, Any

class TrivialBaselineAgent:
    def __init__(self):
        self.majority_intent = "DEVICE_BATTERY_POWER"
        self.trigger_words = ["refund", "broken"]

    def process(self, raw_tweet: str) -> Dict[str, Any]:
        lower = raw_tweet.lower()
        should_escalate = any(w in lower for w in self.trigger_words)

        decision = "ESCALATE" if should_escalate else "AUTO_HANDLE"
        stated_reason = "Trivial keyword match ('refund' or 'broken')" if should_escalate else "Default trivial auto-handle"

        draft_reply = (
            "Thank you for contacting Apple Support. We are sorry for any inconvenience this has caused. "
            "Please try restarting your device or visiting your local store."
        )

        return {
            "query": raw_tweet,
            "predicted_intent": self.majority_intent,
            "intent_confidence": 0.20,
            "decision": decision,
            "should_escalate": should_escalate,
            "stated_reason": stated_reason,
            "draft_reply": draft_reply
        }
