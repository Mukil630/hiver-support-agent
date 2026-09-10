"""
Core Support Agent for @AppleSupport.
Integrates preprocessing, intent classification, grounding retrieval,
escalation decision logic, and brand-aligned response generation.
"""

from typing import Dict, Any, Optional
from .preprocessor import TweetPreprocessor
from .classifier import IntentClassifier
from .retriever import HistoricalRetriever
from .escalation import EscalationEngine

class AppleSupportAgent:
    def __init__(self, confidence_threshold: float = 0.48):
        self.preprocessor = TweetPreprocessor()
        self.classifier = IntentClassifier()
        self.retriever = HistoricalRetriever()
        self.escalator = EscalationEngine(confidence_threshold=confidence_threshold)

    def process(self, raw_tweet: str) -> Dict[str, Any]:
        """
        Full end-to-end inference pipeline for an incoming customer tweet.
        """
        # Step 1: Feature extraction & preprocessing
        features = self.preprocessor.extract_features(raw_tweet)
        cleaned_query = features["cleaned_text"]

        # Step 2: Intent Classification & Confidence estimation
        classification = self.classifier.predict(cleaned_query)
        predicted_intent = classification["top_intent"]
        confidence = classification["confidence"]

        # Step 3: Escalation Decision Matrix & Stated Reason
        escalation = self.escalator.evaluate(
            raw_text=raw_tweet,
            predicted_intent=predicted_intent,
            confidence=confidence,
            features=features
        )

        # Step 4: Historical Grounding Retrieval (RAG)
        retrieved_docs = self.retriever.retrieve(
            query=cleaned_query,
            intent_filter=predicted_intent,
            top_k=2
        )

        # Step 5: Draft Brand-Grounded Reply
        draft_reply = self._generate_reply(
            cleaned_query=cleaned_query,
            predicted_intent=predicted_intent,
            escalation=escalation,
            retrieved_docs=retrieved_docs,
            features=features
        )

        return {
            "query": raw_tweet,
            "cleaned_query": cleaned_query,
            "predicted_intent": predicted_intent,
            "intent_confidence": confidence,
            "is_ambiguous": classification["is_ambiguous"],
            "decision": escalation["decision"],
            "should_escalate": escalation["should_escalate"],
            "stated_reason": escalation["stated_reason"],
            "risk_category": escalation["risk_category"],
            "retrieved_context": retrieved_docs,
            "draft_reply": draft_reply
        }

    def _generate_reply(self,
                        cleaned_query: str,
                        predicted_intent: str,
                        escalation: Dict[str, Any],
                        retrieved_docs: list,
                        features: Dict[str, Any]) -> str:
        """
        Generates brand-compliant Apple Support responses.
        Follows official guidelines:
        - Empathetic acknowledgment
        - Grounded troubleshooting or immediate safety escalation protocol
        - Relevant support.apple.com link
        - Call-to-action (DM for further diagnosis or Genius Bar booking)
        """
        should_escalate = escalation["should_escalate"]
        risk_category = escalation["risk_category"]

        # Top retrieved historical resolution if available
        top_historical = retrieved_docs[0]["historical_resolution"] if retrieved_docs else ""

        if should_escalate:
            if risk_category == "SAFETY_HAZARD":
                return (
                    "Your safety is our absolute priority. Please immediately disconnect the device from any power source "
                    "and place it in a cool, fire-safe area. Do not attempt to charge or use the device. "
                    "Please send us a Direct Message immediately so our executive safety team can prioritize your case."
                )
            elif risk_category in ["HARDWARE_REPAIR", "HARDWARE_DEFECT"]:
                return (
                    "We're sorry to hear about the physical damage to your Apple device. Because hardware issues require hands-on "
                    "diagnostic testing, please schedule a visit with an Apple Authorized Service Provider or book a Genius Bar "
                    "appointment here: https://support.apple.com/repair. You can also send us a DM with your serial number to check AppleCare+ coverage."
                )
            elif risk_category == "LEGAL_COMPLIANCE":
                return (
                    "Thank you for contacting Apple Support. We have flagged your request for priority handling by our senior "
                    "advisory team. Please send us a Direct Message with your case details and contact information so an advisor can connect with you directly."
                )
            elif risk_category == "SECURITY_BREACH":
                return (
                    "Protecting your account and identity is extremely important to us. If you suspect unauthorized activity, "
                    "please visit https://appleid.apple.com immediately to review your active devices and reset your password. "
                    "We are escalating your report to our Account Security specialists—please send us a DM right away so we can assist."
                )
            elif risk_category == "BILLING_DISPUTE":
                return (
                    "We understand how concerning unexpected or contested charges can be. While you can review recent transactions at "
                    "https://reportaproblem.apple.com, our billing investigation team is taking over this ticket. Please DM us your "
                    "Apple ID email and the transaction date so we can investigate."
                )
            else: # MODEL_UNCERTAINTY or general escalation
                return (
                    "We want to make sure you get the exact right assistance for your Apple device. "
                    "We've routed your inquiry to a senior technical specialist. Please send us a Direct Message "
                    "with your current OS version and device model so we can take a closer look."
                )
        else:
            # Auto-handle: Grounded in historical resolution
            if top_historical:
                return top_historical
            else:
                return (
                    "We'd love to help resolve this for you! You can find step-by-step diagnostic guidance at "
                    "https://support.apple.com. If you're still experiencing this issue, send us a Direct Message "
                    "with your device model and iOS version so we can assist further."
                )
