"""TF-IDF relevance scoring implementation with sublinear term scaling and smoothed IDF."""

import math

from aerosearch.core.structures.inverted_index import InvertedIndex


class TFIDFScorer:
    """TF-IDF relevance scorer with sublinear term frequency scaling."""

    def __init__(self, sublinear_tf: bool = True) -> None:
        self.sublinear_tf = sublinear_tf

    def compute_idf(self, n_q: int, total_docs: int) -> float:
        """Compute smoothed IDF: ln((N + 1) / (n_q + 1)) + 1."""
        if total_docs <= 0:
            return 0.0
        return math.log((total_docs + 1.0) / (n_q + 1.0)) + 1.0

    def compute_tf(self, tf: int) -> float:
        """Compute term frequency (sublinear: 1 + ln(tf) for tf > 0)."""
        if tf <= 0:
            return 0.0
        if self.sublinear_tf:
            return 1.0 + math.log(tf)
        return float(tf)

    def score_corpus(
        self,
        query_terms: list[str],
        index: InvertedIndex,
    ) -> dict[str, float]:
        """Score all matching documents using TF-IDF."""
        total_docs = index.total_documents
        if total_docs == 0 or not query_terms:
            return {}

        scores: dict[str, float] = {}

        for term in set(query_terms):
            postings = index.get_postings(term)
            if not postings:
                continue

            n_q = len(postings)
            idf = self.compute_idf(n_q, total_docs)

            for posting in postings:
                tf_val = self.compute_tf(posting.term_frequency)
                scores[posting.doc_id] = scores.get(posting.doc_id, 0.0) + (tf_val * idf)

        return scores
