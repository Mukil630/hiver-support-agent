"""
Intent Classifier with Calibrated Confidence Scoring.
Classifies customer messages into 6 defined Apple Support intents.
"""

import json
import os
import re
import math
from typing import Dict, Any, Tuple, List

class IntentClassifier:
    def __init__(self, schema_path: str = None):
        if schema_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            schema_path = os.path.join(base_dir, "data", "intent_schema.json")
            
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
            
        self.intents = self.schema["intents"]
        
        # Extended weighted keyword dictionaries for robust domain matching
        self.intent_lexicon: Dict[str, Dict[str, float]] = {
            "DEVICE_BATTERY_POWER": {
                "battery": 3.0, "drain": 2.5, "drains": 2.5, "dying": 2.0, "charge": 2.0, 
                "charging": 2.0, "charger": 2.0, "overheating": 2.5, "overheat": 2.5, "hot": 1.8, 
                "warm": 1.2, "battery health": 3.5, "cable": 1.5, "magsafe": 2.0, "dies": 2.0, 
                "percentage": 1.8, "drops": 1.5, "watt": 2.0, "wattage": 2.0, "low power mode": 3.0,
                "clean energy": 3.0, "screen on time": 2.0, "maximum capacity": 3.0, "unplugging": 1.8,
                "lightning port": 2.0, "swollen": 2.5, "spark": 2.0
            },
            "OS_SOFTWARE_UPDATE": {
                "update": 2.5, "updated": 2.5, "updating": 2.5, "ios": 3.0, "ios 17": 3.5, 
                "ios 16": 3.5, "freeze": 2.5, "frozen": 2.5, "lag": 2.0, "lagging": 2.0, 
                "glitch": 2.0, "glitches": 2.0, "crash": 2.0, "crashes": 2.0, "crashing": 2.0, 
                "bootloop": 3.5, "boot loop": 3.5, "apple logo": 2.5, "restore": 2.0, "dfu": 3.0, 
                "itunes": 2.0, "finder": 1.5, "software": 2.0, "keyboard": 1.5, "widgets": 2.0, 
                "standby": 2.5, "spotlight": 2.0, "downgrade": 2.5, "beta": 2.5, "unable to verify": 3.0,
                "storage": 1.5, "system data": 2.0, "springboard": 3.0, "respring": 3.0
            },
            "APPLE_ID_SECURITY": {
                "apple id": 3.5, "icloud": 2.5, "password": 3.0, "passcode": 2.0, "2fa": 3.5, 
                "two-factor": 3.5, "verification code": 3.0, "verification": 2.0, "code": 1.5, 
                "hacked": 3.0, "stolen": 2.5, "lockout": 2.5, "locked": 2.0, "iforgot": 3.5, 
                "phishing": 3.0, "unauthorized": 2.5, "activation lock": 4.0, "recovery key": 3.5, 
                "sim swap": 3.5, "extortion": 3.0, "blackmail": 3.0, "airtag": 2.5, "tracking": 2.0, 
                "stalker": 3.0, "login": 2.0, "sign in": 2.0, "legacy contact": 3.0, "disabled": 2.0,
                "security keys": 3.0, "yubikey": 3.0, "screen time passcode": 2.5, "warrant": 3.0
            },
            "HARDWARE_PHYSICAL_DAMAGE": {
                "cracked": 3.5, "crack": 3.0, "shattered": 3.5, "broken": 3.0, "dropped": 2.5, 
                "toilet": 3.0, "water": 2.5, "liquid": 3.0, "submerged": 3.0, "bent": 3.0, 
                "screen": 2.0, "display": 1.8, "glass": 2.5, "back glass": 3.0, "speaker": 2.0, 
                "microphone": 2.0, "mic": 2.0, "camera lens": 3.0, "camera glass": 3.0, 
                "button": 2.0, "power button": 2.5, "volume button": 2.5, "mute switch": 3.0, 
                "genius bar": 2.5, "repair": 2.5, "technician": 2.0, "green line": 3.5, "ink bleed": 3.5, 
                "taptic engine": 3.0, "vibration rattle": 3.0, "pins": 2.5, "sim tray stuck": 3.0, 
                "dead pixels": 3.5, "truedepth": 3.5, "face id hardware": 3.5, "coffee spilled": 3.0,
                "melted": 3.0, "fire": 2.5, "popping sound": 2.5, "chewed": 3.0
            },
            "SUBSCRIPTION_BILLING": {
                "refund": 3.5, "charged": 3.0, "charge": 2.5, "billing": 3.0, "billed": 3.0, 
                "subscription": 3.5, "sub": 2.0, "cancel": 2.5, "canceling": 2.5, "app store": 2.5, 
                "in-app purchase": 3.0, "apple music": 2.5, "apple tv": 2.5, "apple one": 2.5, 
                "reportaproblem": 3.5, "money": 2.5, "dollar": 2.0, "$": 2.5, "credit card": 2.5, 
                "debit card": 2.5, "bank": 2.0, "unauthorized charge": 3.5, "roblox": 2.5, "coins": 2.0, 
                "fraud": 2.5, "chargeback": 3.5, "pro-rated": 3.0, "trial": 2.0, "gift card": 3.0, 
                "receipt": 2.5, "tax invoice": 2.5, "paypal": 2.5, "deducted": 2.5, "family sharing purchase": 2.5
            },
            "CONNECTIVITY_ACCESSORIES": {
                "wifi": 3.5, "wi-fi": 3.5, "bluetooth": 3.5, "airpods": 3.0, "apple watch": 3.0, 
                "carplay": 3.5, "pairing": 3.0, "pair": 2.5, "connect": 2.0, "connecting": 2.0, 
                "connection": 2.0, "disconnect": 2.5, "disconnects": 2.5, "disconnecting": 2.5, 
                "cellular": 2.0, "signal": 2.0, "no service": 3.0, "sos only": 3.5, "esim": 2.5, 
                "airdrop": 2.5, "namedrop": 2.5, "hotspot": 3.0, "pencil": 2.5, "apple pencil": 3.0, 
                "magic keyboard": 3.0, "greyed out": 2.5, "stutters": 2.0, "controller": 2.5, 
                "dualsense": 3.0, "weak security": 2.5, "5g": 2.0, "wpa3": 3.0, "smart connector": 3.0
            }
        }

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Calculates normalized probability distribution across intents.
        Returns top intent, confidence score, and distribution.
        """
        lower_text = text.lower()
        cleaned_text = re.sub(r"[^a-zA-Z0-9\s$]", " ", lower_text)
        words = set(cleaned_text.split())

        raw_scores: Dict[str, float] = {}
        
        for intent, lexicon in self.intent_lexicon.items():
            score = 0.1 # Prior Laplace smoothing
            for term, weight in lexicon.items():
                if " " in term:
                    # Multi-word phrase search
                    if term in lower_text:
                        score += weight * 2.0
                elif term in words or term in lower_text:
                    score += weight
            raw_scores[intent] = score

        # Softmax normalization with temperature calibration
        temperature = 1.8
        max_score = max(raw_scores.values())
        exp_scores = {k: math.exp((v - max_score) / temperature) for k, v in raw_scores.items()}
        sum_exp = sum(exp_scores.values())
        probabilities = {k: round(v / sum_exp, 4) for k, v in exp_scores.items()}

        sorted_intents = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        top_intent, top_confidence = sorted_intents[0]
        second_intent, second_confidence = sorted_intents[1]

        # Margin analysis
        margin = top_confidence - second_confidence
        is_ambiguous = margin < 0.12

        return {
            "top_intent": top_intent,
            "confidence": top_confidence,
            "is_ambiguous": is_ambiguous,
            "margin": round(margin, 4),
            "second_intent": second_intent,
            "probabilities": probabilities
        }
