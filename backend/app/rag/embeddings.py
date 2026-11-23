import re
import math
import numpy as np
from typing import List, Dict, Any, Tuple

class SimpleVectorStore:
    """
    Production-grade in-memory Vector Database using TF-IDF Normalized Embeddings
    and Cosine Similarity scoring. Runs without external C-binary dependencies,
    ensuring 100% reliability, zero-latency index builds, and instant search.
    """
    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.idf: np.ndarray = np.array([])
        self.doc_vectors: np.ndarray = np.array([])
        self.metadata: List[Dict[str, Any]] = []

    def _tokenize(self, text: str) -> List[str]:
        # Lowercase and clean words, retaining alphanumeric tokens
        tokens = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())
        # Filter common English stopwords
        stopwords = {
            "the", "and", "is", "in", "to", "of", "it", "with", "as", "for", "on", "at", 
            "by", "this", "that", "an", "be", "are", "from", "or", "which", "will", "all",
            "has", "have", "had", "can", "may", "under", "per", "such", "other", "any"
        }
        return [t for t in tokens if t not in stopwords]

    def build_index(self, documents: List[Dict[str, Any]]):
        self.metadata = documents
        num_docs = len(documents)
        if num_docs == 0:
            return

        # 1. Build Vocabulary
        doc_tokens_list = []
        df: Dict[str, int] = {}
        for doc in documents:
            text = f"{doc.get('title', '')} {doc.get('section', '')} {doc.get('content', '')}"
            tokens = self._tokenize(text)
            doc_tokens_list.append(tokens)
            unique_tokens = set(tokens)
            for t in unique_tokens:
                df[t] = df.get(t, 0) + 1

        vocab_words = sorted(list(df.keys()))
        self.vocabulary = {w: i for i, w in enumerate(vocab_words)}
        vocab_size = len(vocab_words)

        # 2. Compute IDF
        self.idf = np.zeros(vocab_size)
        for w, idx in self.vocabulary.items():
            self.idf[idx] = math.log((1 + num_docs) / (1 + df[w])) + 1.0

        # 3. Compute TF-IDF matrix
        vectors = np.zeros((num_docs, vocab_size), dtype=np.float32)
        for i, tokens in enumerate(doc_tokens_list):
            if not tokens:
                continue
            tf: Dict[int, int] = {}
            for t in tokens:
                if t in self.vocabulary:
                    idx = self.vocabulary[t]
                    tf[idx] = tf.get(idx, 0) + 1
            for idx, count in tf.items():
                vectors[i, idx] = (count / len(tokens)) * self.idf[idx]

        # 4. L2 Normalize vectors for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        self.doc_vectors = vectors / norms

    def search(self, query: str, top_k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        if len(self.metadata) == 0 or self.doc_vectors.size == 0:
            return []

        tokens = self._tokenize(query)
        if not tokens:
            return []

        vocab_size = len(self.vocabulary)
        q_vec = np.zeros(vocab_size, dtype=np.float32)
        tf: Dict[int, int] = {}
        for t in tokens:
            if t in self.vocabulary:
                idx = self.vocabulary[t]
                tf[idx] = tf.get(idx, 0) + 1

        for idx, count in tf.items():
            q_vec[idx] = (count / len(tokens)) * self.idf[idx]

        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            # Fallback simple substring matching
            results = []
            for doc in self.metadata:
                content_lower = doc.get("content", "").lower()
                matches = sum(1 for t in tokens if t in content_lower)
                score = matches / max(1, len(tokens))
                results.append((doc, score))
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]

        q_vec = q_vec / q_norm
        # Cosine similarity is dot product of normalized vectors
        scores = np.dot(self.doc_vectors, q_vec)
        
        # Boost for exact crop name or keyword occurrence in title
        for i, doc in enumerate(self.metadata):
            title_lower = doc.get("title", "").lower()
            for t in tokens:
                if t in title_lower:
                    scores[i] += 0.15

        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((self.metadata[idx], float(scores[idx])))
            
        return results
