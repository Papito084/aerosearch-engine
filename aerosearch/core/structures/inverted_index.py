"""Inverted Index data structure for full-text storage and postings retrieval."""

from collections import defaultdict

from aerosearch.core.models import Document, Posting, Token


class InvertedIndex:
    """In-memory Inverted Index tracking document postings, term frequencies, and positions."""

    def __init__(self) -> None:
        # term -> {doc_id: Posting}
        self._postings: dict[str, dict[str, Posting]] = defaultdict(dict)
        # doc_id -> Document
        self._documents: dict[str, Document] = {}
        # doc_id -> total token count
        self._doc_lengths: dict[str, int] = {}
        # Total tokens indexed across all documents
        self._total_tokens: int = 0

    def add_document(self, document: Document, tokens: list[Token]) -> None:
        """Add or update a document in the index."""
        doc_id = document.id

        # If document already exists, remove previous postings first
        if doc_id in self._documents:
            self.remove_document(doc_id)

        self._documents[doc_id] = document
        doc_length = len(tokens)
        self._doc_lengths[doc_id] = doc_length
        self._total_tokens += doc_length

        # Aggregate positions and frequencies per term
        term_positions: dict[str, list[int]] = defaultdict(list)
        for token in tokens:
            term_positions[token.stemmed].append(token.position)

        for term, positions in term_positions.items():
            self._postings[term][doc_id] = Posting(
                doc_id=doc_id,
                term_frequency=len(positions),
                positions=positions,
            )

    def remove_document(self, doc_id: str) -> bool:
        """Remove a document and its postings from the index."""
        if doc_id not in self._documents:
            return False

        old_length = self._doc_lengths.pop(doc_id, 0)
        self._total_tokens -= old_length
        del self._documents[doc_id]

        # Clean postings
        terms_to_delete = []
        for term, doc_dict in self._postings.items():
            if doc_id in doc_dict:
                del doc_dict[doc_id]
                if not doc_dict:
                    terms_to_delete.append(term)

        for term in terms_to_delete:
            del self._postings[term]

        return True

    def get_document(self, doc_id: str) -> Document | None:
        """Retrieve full document by id."""
        return self._documents.get(doc_id)

    def get_postings(self, term: str) -> list[Posting]:
        """Get list of postings for a specific stemmed term."""
        doc_dict = self._postings.get(term)
        if not doc_dict:
            return []
        return list(doc_dict.values())

    def get_document_frequency(self, term: str) -> int:
        """Number of documents containing term (n_q)."""
        doc_dict = self._postings.get(term)
        return len(doc_dict) if doc_dict else 0

    def get_doc_length(self, doc_id: str) -> int:
        """Length of document in tokens."""
        return self._doc_lengths.get(doc_id, 0)

    @property
    def total_documents(self) -> int:
        """Total number of documents indexed (N)."""
        return len(self._documents)

    @property
    def total_unique_terms(self) -> int:
        """Total number of distinct vocabulary terms."""
        return len(self._postings)

    @property
    def total_postings(self) -> int:
        """Total number of postings across all terms."""
        return sum(len(d) for d in self._postings.values())

    @property
    def total_tokens(self) -> int:
        """Total number of tokens indexed."""
        return self._total_tokens

    @property
    def avg_doc_length(self) -> float:
        """Average document length across the indexed corpus (avgdl)."""
        if not self._documents:
            return 0.0
        return self._total_tokens / len(self._documents)

    def get_all_doc_ids(self) -> list[str]:
        """Return list of all indexed document IDs."""
        return list(self._documents.keys())
