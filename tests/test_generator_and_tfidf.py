"""Unit tests for demo data generator and TF-IDF scoring."""

from aerosearch.core.scoring.tfidf import TFIDFScorer
from aerosearch.core.structures.inverted_index import InvertedIndex
from aerosearch.core.text.tokenizer import Tokenizer
from aerosearch.data.generator import generate_demo_documents


def test_generator_output() -> None:
    docs = generate_demo_documents(count=20, seed=123)
    assert len(docs) == 20
    for doc in docs:
        assert doc.id.startswith("aero-doc-")
        assert len(doc.title) > 0
        assert len(doc.content) > 50
        assert len(doc.tags) > 0
        assert "author" in doc.metadata


def test_tfidf_scorer() -> None:
    index = InvertedIndex()
    tokenizer = Tokenizer()
    docs = generate_demo_documents(count=10, seed=42)
    for doc in docs:
        tokens = tokenizer.tokenize(f"{doc.title} {doc.content}")
        index.add_document(doc, tokens)

    scorer = TFIDFScorer()
    scores = scorer.score_corpus(["propulsion"], index)
    assert isinstance(scores, dict)
    if scores:
        top_doc_id = max(scores, key=lambda k: scores[k])
        assert scores[top_doc_id] > 0
