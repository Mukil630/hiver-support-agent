"""
Historical Grounding Knowledge Base Retriever.
Uses TF-IDF Vector Space Model & Cosine Similarity to retrieve historically grounded
Apple Support resolutions, official KB article links, and diagnostic protocols.
"""

import json
import os
import re
import math
from typing import List, Dict, Any

class HistoricalRetriever:
    def __init__(self, kb_path: str = None):
        if kb_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            kb_path = os.path.join(base_dir, "data", "apple_support_kb.jsonl")
        
        self.kb_path = kb_path
        self.corpus: List[Dict[str, Any]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_vectors: List[Dict[int, float]] = []
        self._load_and_index()

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        tokens = cleaned.split()
        # Include unigrams + bigrams for better phrase matching
        n_grams = list(tokens)
        for i in range(len(tokens) - 1):
            n_grams.append(f"{tokens[i]}_{tokens[i+1]}")
        return n_grams

    def _load_and_index(self):
        """Loads historical resolution pairs and computes TF-IDF representations."""
        if not os.path.exists(self.kb_path):
            raise FileNotFoundError(f"Knowledge Base not found at {self.kb_path}")

        with open(self.kb_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    self.corpus.append(json.loads(line.strip()))

        N = len(self.corpus)
        doc_term_freqs = []
        term_doc_count: Dict[str, int] = {}

        # 1. Build Document Frequencies
        for doc in self.corpus:
            combined_text = f"{doc['sample_query']} {doc['intent']} {' '.join(doc.get('key_actions', []))}"
            tokens = self._tokenize(combined_text)
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            doc_term_freqs.append(tf)

            for term in tf.keys():
                term_doc_count[term] = term_doc_count.get(term, 0) + 1

        # 2. Build Vocabulary and IDF
        for idx, (term, count) in enumerate(term_doc_count.items()):
            self.vocabulary[term] = idx
            self.idf[term] = math.log((N + 1.0) / (count + 1.0)) + 1.0

        # 3. Build TF-IDF Vectors
        for tf in doc_term_freqs:
            vector: Dict[int, float] = {}
            norm = 0.0
            for term, freq in tf.items():
                tid = self.vocabulary[term]
                val = (1.0 + math.log(freq)) * self.idf[term]
                vector[tid] = val
                norm += val * val
            
            norm = math.sqrt(norm) if norm > 0 else 1.0
            for tid in vector:
                vector[tid] /= norm
            self.doc_vectors.append(vector)

    def retrieve(self, query: str, intent_filter: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves top-K most relevant historical resolutions for a query."""
        tokens = self._tokenize(query)
        q_tf: Dict[str, int] = {}
        for t in tokens:
            if t in self.vocabulary:
                q_tf[t] = q_tf.get(t, 0) + 1

        if not q_tf:
            # Fallback to intent matches if no term overlaps
            return [doc for doc in self.corpus if doc["intent"] == intent_filter][:top_k] if intent_filter else self.corpus[:top_k]

        # Vectorize query
        q_vec: Dict[int, float] = {}
        norm = 0.0
        for term, freq in q_tf.items():
            tid = self.vocabulary[term]
            val = (1.0 + math.log(freq)) * self.idf[term]
            q_vec[tid] = val
            norm += val * val
        
        norm = math.sqrt(norm) if norm > 0 else 1.0
        for tid in q_vec:
            q_vec[tid] /= norm

        # Compute cosine similarity
        scores = []
        for doc_idx, doc_vec in enumerate(self.doc_vectors):
            doc = self.corpus[doc_idx]
            
            # Boost score if intent matches
            intent_boost = 1.3 if (intent_filter and doc["intent"] == intent_filter) else 1.0

            dot_product = 0.0
            for tid, val in q_vec.items():
                if tid in doc_vec:
                    dot_product += val * doc_vec[tid]
            
            final_score = dot_product * intent_boost
            scores.append((final_score, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, doc in scores[:top_k]:
            results.append({
                "similarity_score": round(score, 4),
                "intent": doc["intent"],
                "historical_query": doc["sample_query"],
                "historical_resolution": doc["resolution_text"],
                "key_actions": doc.get("key_actions", [])
            })
        return results
