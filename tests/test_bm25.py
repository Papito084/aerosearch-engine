"""Unit tests for Okapi BM25 ranking algorithm with manual verification."""

import math

import pytest

from aerosearch.core.models import Document, Token
from aerosearch.core.scoring.bm25 import BM25Scorer
from aerosearch.core.structures.inverted_index import InvertedIndex


def test_bm25_manual_calculation() -> None:
    scorer = BM25Scorer(k1=1.2, b=0.75)

    # 1. Manual check of IDF formula
    # N = 3, n(q) = 2
    # IDF = ln(1 + (3 - 2 + 0.5) / (2 + 0.5)) = ln(1 + 1.5 / 2.5) = ln(1.6)
    expected_idf = math.log(1.0 + 1.5 / 2.5)
    calculated_idf = scorer.compute_idf(n_q=2, total_docs=3)
    assert calculated_idf == pytest.approx(expected_idf, rel=1e-6)

    # 2. Manual check of Document score
    # Setup index with known lengths and term counts
    index = InvertedIndex()

    # Doc 1: length 10, contains term 'query' 2 times
    doc1 = Document(id="d1", title="title1", content="content1")
    tokens1 = [Token("query", "query", "query", i) for i in range(2)] + [
        Token("word", "word", "word", i) for i in range(2, 10)
    ]

    # Doc 2: length 20, contains term 'query' 1 time
    doc2 = Document(id="d2", title="title2", content="content2")
    tokens2 = [Token("query", "query", "query", 0)] + [
        Token("word", "word", "word", i) for i in range(1, 20)
    ]

    # Doc 3: length 10, contains term 'query' 0 times
    doc3 = Document(id="d3", title="title3", content="content3")
    tokens3 = [Token("word", "word", "word", i) for i in range(10)]

    index.add_document(doc1, tokens1)
    index.add_document(doc2, tokens2)
    index.add_document(doc3, tokens3)

    assert index.total_documents == 3
    assert index.avg_doc_length == (10 + 20 + 10) / 3.0  # 40 / 3

    # Theoretical manual BM25 calculation for doc1:
    # avgdl = 40 / 3
    # len_norm = 1 - 0.75 + 0.75 * (10 / (40 / 3)) = 0.25 + 0.75 * 0.75 = 0.8125
    # tf = 2, k1 = 1.2
    # tf_comp = 2 * (1.2 + 1) / (2 + 1.2 * 0.8125) = 4.4 / 2.975 = 1.4789915966386553
    # expected_score = expected_idf * tf_comp
    avgdl = 40.0 / 3.0
    len_norm_d1 = 1.0 - 0.75 + 0.75 * (10.0 / avgdl)
    tf_comp_d1 = (2.0 * 2.2) / (2.0 + 1.2 * len_norm_d1)
    expected_doc1_score = expected_idf * tf_comp_d1

    computed_score = scorer.score_document(query_terms=["query"], doc_id="d1", index=index)
    assert computed_score == pytest.approx(expected_doc1_score, rel=1e-5)

    # Doc 1 has higher TF and shorter length than Doc 2, so its BM25 score must be strictly greater
    doc2_score = scorer.score_document(query_terms=["query"], doc_id="d2", index=index)
    assert computed_score > doc2_score
