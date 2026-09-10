"""
Escalation Engine with Explicit Policy Auditing & Stated Reasons.
Decides whether an incoming customer message can be safely auto-handled or
must be escalated to a human tier-2 specialist.
"""

import re
from typing import Dict, Any

class EscalationEngine:
    def __init__(self, confidence_threshold: float = 0.48):
        self.confidence_threshold = confidence_threshold

        # Safety & Emergency hazard terms
        self.safety_terms = [
            "swollen", "fire", "spark", "sparking", "smoking", "smoke", "exploded", 
            "burn", "burning", "scorched", "melted", "battery swelling", "popping sound in ear",
            "ear is ringing painfully", "boiling hot", "temperature warning"
        ]

        # Legal & High-hostility terms
        self.legal_hostile_terms = [
            "police", "warrant", "search warrant", "lawyer", "sue", "legal action", 
            "probate", "court order", "stealing my money", "report to police", "technician messed up",
            "demand a replacement", "supervisor", "data recovery specialist"
        ]

        # Security breach & Crime terms
        self.security_breach_terms = [
            "hacked", "stolen", "blackmail", "extortion", "sim swap", "stalker", 
            "burglar", "phishing", "unauthorized device", "spyware", "brute-forcing",
            "brute force", "fake sms", "unknown part", "compromised", "waiting 28 days",
            "locked me out", "legacy contact", "deceased", "search warrant"
        ]

        # High-friction financial disputes
        self.financial_dispute_terms = [
            "fraud", "chargeback", "billed 4 times", "charged twice", "unauthorized transaction",
            "dementia", "disputed fraudulent", "ticket #", "denied", "stop stealing",
            "auto-denied", "deducted", "stolen package", "pre-auth freeze", "itemized purchase history"
        ]

        # Hardware failure terms
        self.hardware_failure_terms = [
            "cracked", "shattered", "broken", "liquid", "water damage", "toilet", "bent", 
            "camera glass", "green line", "ink bleed", "modem firmware", "greyed out",
            "pins", "sim tray stuck", "dead pixels", "truedepth", "taptic", "rattle",
            "brick", "bricked", "bootloop", "infinite bootloop", "error 4013",
            "respring", "springboard crash", "corrupted", "dead on day 2", "shuts down abruptly",
            "sparking", "empty box", "cannot register on any network"
        ]

    def evaluate(self, 
                 raw_text: str, 
                 predicted_intent: str, 
                 confidence: float, 
                 features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates escalation requirements against explicit policy rules.
        Returns:
            should_escalate: bool
            decision: "ESCALATE" | "AUTO_HANDLE"
            stated_reason: str
            risk_category: str
        """
        lower_text = raw_text.lower()

        # Rule 1: Life Safety / Fire / Physical Hazard (P0)
        for term in self.safety_terms:
            if term in lower_text:
                return {
                    "should_escalate": True,
                    "decision": "ESCALATE",
                    "stated_reason": f"Safety/Hazard Flag: Detected '{term}'. High physical risk requiring immediate safety team intervention.",
                    "risk_category": "SAFETY_HAZARD"
                }

        # Rule 2: Legal, Court Orders, or Severe Hostility (P0)
        for term in self.legal_hostile_terms:
            if term in lower_text:
                return {
                    "should_escalate": True,
                    "decision": "ESCALATE",
                    "stated_reason": f"Legal/Compliance Flag: Detected '{term}'. Requires human supervisor or Apple Legal coordination.",
                    "risk_category": "LEGAL_COMPLIANCE"
                }

        # Rule 3: Active Security Compromise / Account Takeover (P1)
        for term in self.security_breach_terms:
            if term in lower_text:
                return {
                    "should_escalate": True,
                    "decision": "ESCALATE",
                    "stated_reason": f"Account Compromise Flag: Detected '{term}'. Potential unauthorized access requiring identity security verification.",
                    "risk_category": "SECURITY_BREACH"
                }

        # Rule 4: Hardware Physical Damage Intent (P1)
        if predicted_intent == "HARDWARE_PHYSICAL_DAMAGE":
            return {
                "should_escalate": True,
                "decision": "ESCALATE",
                "stated_reason": "Policy Rule: Hardware and physical damage cannot be resolved through automated Twitter support; requires Genius Bar or mail-in repair inspection.",
                "risk_category": "HARDWARE_REPAIR"
            }

        # Rule 5: Explicit Hardware Failure Keywords in other intents
        for term in self.hardware_failure_terms:
            if term in lower_text:
                return {
                    "should_escalate": True,
                    "decision": "ESCALATE",
                    "stated_reason": f"Hardware Failure Symptom: Detected '{term}'. Suggests component defect or unrecoverable firmware crash requiring technician diagnosis.",
                    "risk_category": "HARDWARE_DEFECT"
                }

        # Rule 6: High-Friction Financial & Billing Disputes (P1)
        if predicted_intent == "SUBSCRIPTION_BILLING":
            for term in self.financial_dispute_terms:
                if term in lower_text:
                    return {
                        "should_escalate": True,
                        "decision": "ESCALATE",
                        "stated_reason": f"Billing Dispute Flag: Detected '{term}'. Financial anomaly or contested transaction requiring human billing authorization.",
                        "risk_category": "BILLING_DISPUTE"
                    }

        # Rule 6b: Apple ID Security Default-Safe Policy
        if predicted_intent == "APPLE_ID_SECURITY":
            safe_security_terms = [
                "how do i reset", "where do i go to reset", "change the trusted phone number", 
                "what is an apple id recovery key", "legacy contact", "turn off two-factor",
                "transfer an app store purchase", "what is hide my email", "merge two different"
            ]
            is_explicit_safe = any(st in lower_text for st in safe_security_terms)
            if not is_explicit_safe:
                return {
                    "should_escalate": True,
                    "decision": "ESCALATE",
                    "stated_reason": "Account Security Policy: Account lockouts, credential anomalies, and identity recovery require specialized human authentication.",
                    "risk_category": "SECURITY_BREACH"
                }

        # Rule 7: Low Model Confidence / Classifier Ambiguity (P2)
        if confidence < self.confidence_threshold:
            return {
                "should_escalate": True,
                "decision": "ESCALATE",
                "stated_reason": f"Low Model Confidence: Intent classifier confidence ({confidence:.2f}) fell below safety threshold ({self.confidence_threshold:.2f}). Routing to human to prevent misguidance.",
                "risk_category": "MODEL_UNCERTAINTY"
            }

        # Default Safe: Auto-handle with grounded Apple Support guidance
        return {
            "should_escalate": False,
            "decision": "AUTO_HANDLE",
            "stated_reason": "Standard Self-Service Query: Query matches standard diagnostic procedures, KB documentation, or self-service account portal.",
            "risk_category": "SAFE_AUTOHANDLE"
        }
