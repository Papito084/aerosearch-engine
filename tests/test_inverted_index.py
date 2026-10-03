"""Unit tests for InvertedIndex data structure."""

from aerosearch.core.models import Document
from aerosearch.core.structures.inverted_index import InvertedIndex
from aerosearch.core.text.tokenizer import Tokenizer


def test_inverted_index_add_and_query() -> None:
    index = InvertedIndex()
    tokenizer = Tokenizer(enable_stemming=True, enable_stopwords=True)

    doc1 = Document(
        id="doc-1",
        title="Raft Distributed Consensus",
        content="Raft algorithm is designed for consensus in distributed networks.",
    )
    doc2 = Document(
        id="doc-2",
        title="Paxos Protocol",
        content="Paxos consensus protocol provides state replication.",
    )

    tokens1 = tokenizer.tokenize(f"{doc1.title} {doc1.content}")
    tokens2 = tokenizer.tokenize(f"{doc2.title} {doc2.content}")

    index.add_document(doc1, tokens1)
    index.add_document(doc2, tokens2)

    assert index.total_documents == 2
    assert index.total_unique_terms > 0

    # Stemmed "consensus" should appear in both documents
    stemmed_consensus = tokenizer.stemmer.stem("consensus")
    postings = index.get_postings(stemmed_consensus)
    doc_ids = {p.doc_id for p in postings}
    assert doc_ids == {"doc-1", "doc-2"}
    assert index.get_document_frequency(stemmed_consensus) == 2


def test_inverted_index_removal() -> None:
    index = InvertedIndex()
    tokenizer = Tokenizer()
    doc = Document(id="d1", title="Test", content="Sample content")
    tokens = tokenizer.tokenize("sample content")

    index.add_document(doc, tokens)
    assert index.total_documents == 1

    removed = index.remove_document("d1")
    assert removed is True
    assert index.total_documents == 0
    assert index.total_tokens == 0
