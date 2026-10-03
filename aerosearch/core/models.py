"""Core models and abstractions for AeroSearch."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Document:
    """Represents an indexed document in AeroSearch."""

    id: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Token:
    """Represents an analyzed token extracted from text."""

    raw: str
    normalized: str
    stemmed: str
    position: int
    field_name: str = "content"


@dataclass(slots=True)
class Posting:
    """Posting entry in the inverted index for a single term in a document."""

    doc_id: str
    term_frequency: int
    positions: list[int] = field(default_factory=list)


@dataclass(slots=True)
class SearchResultItem:
    """Individual search match item returned to callers."""

    doc_id: str
    title: str
    content: str
    tags: list[str]
    metadata: dict[str, Any]
    score: float
    highlight: str
    matched_terms: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SearchResponse:
    """Aggregated search response including metadata and pagination."""

    query: str
    total_hits: int
    page: int
    limit: int
    total_pages: int
    execution_time_ms: float
    results: list[SearchResultItem]
    did_you_mean: str | None = None


@dataclass(slots=True)
class AutocompleteItem:
    """Single autocomplete suggestion with frequency count."""

    term: str
    frequency: int


@dataclass(slots=True)
class AutocompleteResponse:
    """Autocomplete query response."""

    prefix: str
    suggestions: list[AutocompleteItem]
    execution_time_ms: float


@dataclass(slots=True)
class EngineStats:
    """Real-time diagnostic and operational statistics."""

    total_documents: int
    total_unique_terms: int
    total_postings: int
    avg_doc_length: float
    memory_usage_mb: float
    uptime_seconds: float
