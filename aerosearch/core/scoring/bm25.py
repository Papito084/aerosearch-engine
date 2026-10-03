"""Okapi BM25 relevance scoring algorithm implementation."""

import math

from aerosearch.core.structures.inverted_index import InvertedIndex


class BM25Scorer:
    """Okapi BM25 relevance ranking engine with Robertson-Spärck Jones smoothed IDF."""

    def __init__(self, k1: float = 1.2, b: float = 0.75) -> None:
        """Initialize BM25 with tuneable parameters.

        Args:
            k1: Term frequency saturation parameter (typically between 1.2 and 2.0).
            b: Document length normalization parameter (0.0 = no normalization, 1.0 = full).
        """
        self.k1 = k1
        self.b = b

    def compute_idf(self, n_q: int, total_docs: int) -> float:
        """Calculate smoothed Robertson-Spärck Jones Inverse Document Frequency (IDF).

        Formula:
            IDF(q) = ln(1 + (N - n(q) + 0.5) / (n(q) + 0.5))
        Guarantees non-negative IDF even for terms appearing in > 50% of documents.
        """
        if total_docs <= 0 or n_q <= 0:
            return 0.0
        return math.log(1.0 + (total_docs - n_q + 0.5) / (n_q + 0.5))

    def score_document(
        self,
        query_terms: list[str],
        doc_id: str,
        index: InvertedIndex,
    ) -> float:
        """Compute the BM25 relevance score of a specific document for given query terms."""
        total_docs = index.total_documents
        avgdl = index.avg_doc_length

        if total_docs == 0 or avgdl == 0.0:
            return 0.0

        doc_len = index.get_doc_length(doc_id)
        len_norm = 1.0 - self.b + self.b * (doc_len / avgdl)

        total_score = 0.0
        for term in query_terms:
            n_q = index.get_document_frequency(term)
            if n_q == 0:
                continue

            idf = self.compute_idf(n_q, total_docs)

            # Find term frequency in doc_id
            postings = index.get_postings(term)
            tf = 0
            for p in postings:
                if p.doc_id == doc_id:
                    tf = p.term_frequency
                    break

            if tf == 0:
                continue

            tf_component = (tf * (self.k1 + 1.0)) / (tf + self.k1 * len_norm)
            total_score += idf * tf_component

        return total_score

    def score_corpus(
        self,
        query_terms: list[str],
        index: InvertedIndex,
        title_boost: float = 1.5,
    ) -> dict[str, float]:
        """Compute BM25 scores for all matching documents across the index.

        Utilizes inverted postings lists to skip documents that do not contain any query term.
        """
        total_docs = index.total_documents
        avgdl = index.avg_doc_length

        if total_docs == 0 or avgdl == 0.0 or not query_terms:
            return {}

        scores: dict[str, float] = {}

        for term in set(query_terms):
            postings = index.get_postings(term)
            if not postings:
                continue

            n_q = len(postings)
            idf = self.compute_idf(n_q, total_docs)

            for posting in postings:
                doc_id = posting.doc_id
                doc_len = index.get_doc_length(doc_id)
                len_norm = 1.0 - self.b + self.b * (doc_len / avgdl)
                tf = posting.term_frequency

                tf_component = (tf * (self.k1 + 1.0)) / (tf + self.k1 * len_norm)
                score_contribution = idf * tf_component

                # Optional title boost: check if term appears in title
                doc = index.get_document(doc_id)
                if doc and term in doc.title.lower():
                    score_contribution *= title_boost

                scores[doc_id] = scores.get(doc_id, 0.0) + score_contribution

        return scores
