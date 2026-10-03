"""AeroSearchEngine: Thread-safe, high-performance in-memory Full-Text Search Engine."""

import math
import os
import time

import psutil

from aerosearch.core.models import (
    AutocompleteItem,
    AutocompleteResponse,
    Document,
    EngineStats,
    SearchResponse,
    SearchResultItem,
)
from aerosearch.core.scoring.bm25 import BM25Scorer
from aerosearch.core.scoring.highlighter import HitHighlighter
from aerosearch.core.scoring.tfidf import TFIDFScorer
from aerosearch.core.structures.fuzzy import TrieFuzzyMatcher
from aerosearch.core.structures.inverted_index import InvertedIndex
from aerosearch.core.structures.rwlock import RWLock
from aerosearch.core.structures.trie import Trie
from aerosearch.core.text.stemmer import PorterStemmer
from aerosearch.core.text.stopwords import StopWordsFilter
from aerosearch.core.text.tokenizer import Tokenizer


class AeroSearchEngine:
    """Enterprise-grade pure algorithmic in-memory Full-Text Search Engine."""

    def __init__(
        self,
        languages: list[str] | None = None,
        enable_stemming: bool = True,
        enable_stopwords: bool = True,
        bm25_k1: float = 1.2,
        bm25_b: float = 0.75,
        snippet_length: int = 180,
    ) -> None:
        self.rwlock = RWLock()
        self.index = InvertedIndex()
        self.trie = Trie()
        self.fuzzy_matcher = TrieFuzzyMatcher(self.trie)

        self.stopwords_filter = StopWordsFilter(languages=languages, enabled=enable_stopwords)
        self.stemmer = PorterStemmer()
        self.tokenizer = Tokenizer(
            stopwords_filter=self.stopwords_filter,
            stemmer=self.stemmer,
            enable_stemming=enable_stemming,
            enable_stopwords=enable_stopwords,
        )

        self.bm25 = BM25Scorer(k1=bm25_k1, b=bm25_b)
        self.tfidf = TFIDFScorer()
        self.highlighter = HitHighlighter(snippet_length=snippet_length)

        self._start_time = time.time()
        self._process = psutil.Process(os.getpid()) if psutil else None

    def index_document(self, doc: Document) -> None:
        """Index a single document with thread safety."""
        with self.rwlock.write_lock():
            self._index_document_internal(doc)

    def index_documents(self, docs: list[Document]) -> int:
        """Bulk index a list of documents in a single atomic write transaction."""
        with self.rwlock.write_lock():
            count = 0
            for doc in docs:
                self._index_document_internal(doc)
                count += 1
            return count

    def _index_document_internal(self, doc: Document) -> None:
        """Internal un-synchronized indexing logic."""
        # Aggregate text: title (weighted), tags, and content
        full_text = f"{doc.title} {doc.title} {' '.join(doc.tags)} {doc.content}"
        tokens = self.tokenizer.tokenize(full_text)

        # Update inverted index
        self.index.add_document(doc, tokens)

        # Update Trie with raw terms and frequencies
        for token in tokens:
            self.trie.insert(token.normalized, frequency=1)

    def remove_document(self, doc_id: str) -> bool:
        """Remove a document by ID."""
        with self.rwlock.write_lock():
            return self.index.remove_document(doc_id)

    def search(
        self,
        query: str,
        page: int = 1,
        limit: int = 10,
        scoring: str = "bm25",
    ) -> SearchResponse:
        """Execute full-text search with relevance ranking, snippet highlighting, and timing."""
        start_ns = time.perf_counter_ns()

        if page < 1:
            page = 1
        if limit < 1:
            limit = 10

        query_str = query.strip()
        if not query_str:
            execution_time_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
            return SearchResponse(
                query=query,
                total_hits=0,
                page=page,
                limit=limit,
                total_pages=0,
                execution_time_ms=round(execution_time_ms, 3),
                results=[],
            )

        with self.rwlock.read_lock():
            query_tokens = self.tokenizer.tokenize_query(query_str)
            raw_terms = [t.normalized for t in query_tokens]
            stemmed_terms = [t.stemmed for t in query_tokens]

            if not stemmed_terms:
                execution_time_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
                return SearchResponse(
                    query=query,
                    total_hits=0,
                    page=page,
                    limit=limit,
                    total_pages=0,
                    execution_time_ms=round(execution_time_ms, 3),
                    results=[],
                )

            # Score documents
            if scoring.lower() == "tfidf":
                doc_scores = self.tfidf.score_corpus(stemmed_terms, self.index)
            else:
                doc_scores = self.bm25.score_corpus(stemmed_terms, self.index)

            # Check if typo suggestion is warranted
            did_you_mean: str | None = None
            if not doc_scores:
                suggested_words = []
                for term in raw_terms:
                    correction = self.fuzzy_matcher.suggest_correction(term, max_distance=2)
                    if correction and correction != term:
                        suggested_words.append(correction)
                    else:
                        suggested_words.append(term)
                candidate = " ".join(suggested_words)
                if candidate != query_str.lower():
                    did_you_mean = candidate

            total_hits = len(doc_scores)
            total_pages = math.ceil(total_hits / limit) if total_hits > 0 else 0

            # Sort descending by score
            sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

            # Slice page
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paged_docs = sorted_docs[start_idx:end_idx]

            # Build result items with snippets and highlighting
            items: list[SearchResultItem] = []
            for doc_id, score in paged_docs:
                doc = self.index.get_document(doc_id)
                if not doc:
                    continue

                snippet = self.highlighter.generate_snippet(doc.content, raw_terms)
                items.append(
                    SearchResultItem(
                        doc_id=doc.id,
                        title=doc.title,
                        content=doc.content,
                        tags=doc.tags,
                        metadata=doc.metadata,
                        score=round(score, 4),
                        highlight=snippet,
                        matched_terms=raw_terms,
                    )
                )

            execution_time_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0

            return SearchResponse(
                query=query,
                total_hits=total_hits,
                page=page,
                limit=limit,
                total_pages=total_pages,
                execution_time_ms=round(execution_time_ms, 3),
                results=items,
                did_you_mean=did_you_mean,
            )

    def autocomplete(self, prefix: str, limit: int = 8) -> AutocompleteResponse:
        """Return autocomplete suggestions for a given prefix in real-time."""
        start_ns = time.perf_counter_ns()
        clean_prefix = prefix.strip().lower()

        with self.rwlock.read_lock():
            suggestions_raw = self.trie.autocomplete(clean_prefix, limit=limit)
            suggestions = [
                AutocompleteItem(term=term, frequency=freq) for term, freq in suggestions_raw
            ]

        execution_time_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
        return AutocompleteResponse(
            prefix=prefix,
            suggestions=suggestions,
            execution_time_ms=round(execution_time_ms, 3),
        )

    def get_stats(self) -> EngineStats:
        """Return real-time operational statistics and memory metrics."""
        with self.rwlock.read_lock():
            total_docs = self.index.total_documents
            total_terms = self.index.total_unique_terms
            total_postings = self.index.total_postings
            avgdl = self.index.avg_doc_length

        mem_mb = 0.0
        if self._process:
            try:
                mem_mb = self._process.memory_info().rss / (1024 * 1024)
            except Exception:
                mem_mb = 0.0

        uptime = time.time() - self._start_time

        return EngineStats(
            total_documents=total_docs,
            total_unique_terms=total_terms,
            total_postings=total_postings,
            avg_doc_length=round(avgdl, 2),
            memory_usage_mb=round(mem_mb, 2),
            uptime_seconds=round(uptime, 2),
        )
