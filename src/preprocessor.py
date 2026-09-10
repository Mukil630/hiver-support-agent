"""
Text Preprocessor for Twitter Customer Support Messages.
Handles handle stripping, URL extraction, sentiment/urgency feature extraction.
"""

import re
from typing import Dict, Any

class TweetPreprocessor:
    def __init__(self):
        self.emergency_keywords = [
            "swollen", "fire", "spark", "sparking", "smoking", "smoke", "exploded", "exploding", "explode",
            "burn", "burning", "scorched", "melted", "police", "legal", "lawyer", "sue", "stolen", "hacked", "fraud", 
            "blackmail", "extortion", "urgent", "emergency", "dementia", "warrant"
        ]
        self.hostility_indicators = [
            "trash", "worst", "hate", "pathetic", "useless", "steal", "stealing", 
            "scam", "thieves", "demand", "furious", "unacceptable", "terrible"
        ]
        self.device_patterns = [
            r"iphone\s*(?:1[1-6]|[xX][sSrR]?|[78])(?:\s*pro(?:\s*max)?|\s*plus|\s*mini)?",
            r"ipad\s*(?:pro|air|mini)?",
            r"macbook\s*(?:pro|air)?",
            r"apple\s*watch\s*(?:ultra|series\s*\d+|se)?",
            r"airpods\s*(?:pro(?:\s*2)?|max)?"
        ]

    def clean_text(self, text: str) -> str:
        """Strips Twitter @mentions and normalizes whitespace."""
        cleaned = re.sub(r"@[A-Za-z0-9_]+", "", text)
        cleaned = re.sub(r"https?://\S+", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def extract_features(self, raw_text: str) -> Dict[str, Any]:
        """Extracts conversational features used for risk & escalation scoring."""
        cleaned_text = self.clean_text(raw_text)
        lower_raw = raw_text.lower()
        lower_cleaned = cleaned_text.lower()

        # Check for ALL CAPS screaming
        words = raw_text.split()
        caps_words = [w for w in words if w.isupper() and len(w) > 2 and w.isalpha()]
        is_shouting = len(caps_words) >= 3 or (len(words) > 0 and len(caps_words) / len(words) > 0.4)

        # Detect emergency or safety keywords
        has_emergency = any(kw in lower_raw for kw in self.emergency_keywords)
        
        # Detect hostile sentiment
        has_hostile = any(hk in lower_raw for hk in self.hostility_indicators)

        # Detect device mentions
        detected_devices = []
        for pat in self.device_patterns:
            matches = re.findall(pat, lower_raw)
            if matches:
                detected_devices.extend(matches)
        
        # Punctuation distress (!? multiple exclamation marks)
        has_distress_punct = bool(re.search(r"[!?]{2,}", raw_text))

        return {
            "cleaned_text": cleaned_text,
            "raw_text": raw_text,
            "is_shouting": is_shouting,
            "has_emergency_keyword": has_emergency,
            "has_hostile_sentiment": has_hostile,
            "has_distress_punct": has_distress_punct,
            "detected_devices": list(set(detected_devices)),
            "char_length": len(cleaned_text),
            "word_count": len(cleaned_text.split())
        }
