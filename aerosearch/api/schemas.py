"""Pydantic schemas for the AeroSearch HTTP API."""

from typing import Any

from pydantic import BaseModel, Field


class DocumentIn(BaseModel):
    """Document payload for indexing."""

    id: str = Field(
        ..., description="Unique document identifier", json_schema_extra={"example": "doc-101"}
    )
    title: str = Field(
        ...,
        description="Document title",
        json_schema_extra={"example": "Distributed Consensus with Raft"},
    )
    content: str = Field(
        ...,
        description="Full text document content",
        json_schema_extra={"example": "Raft manages a replicated log..."},
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Categorization tags",
        json_schema_extra={"example": ["distributed-systems"]},
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata fields")


class BulkIndexRequest(BaseModel):
    """Batch document ingestion request."""

    documents: list[DocumentIn] = Field(..., min_length=1, description="List of documents to index")


class BulkIndexResponse(BaseModel):
    """Response returned after bulk ingestion."""

    indexed_count: int
    message: str


class SearchResultItemOut(BaseModel):
    """Single search result item."""

    doc_id: str
    title: str
    content: str
    tags: list[str]
    metadata: dict[str, Any]
    score: float
    highlight: str
    matched_terms: list[str]


class SearchResponseOut(BaseModel):
    """Full-text search response schema."""

    query: str
    total_hits: int
    page: int
    limit: int
    total_pages: int
    execution_time_ms: float
    results: list[SearchResultItemOut]
    did_you_mean: str | None = None


class AutocompleteItemOut(BaseModel):
    """Autocomplete candidate term with frequency."""

    term: str
    frequency: int


class AutocompleteResponseOut(BaseModel):
    """Autocomplete suggestions response schema."""

    prefix: str
    suggestions: list[AutocompleteItemOut]
    execution_time_ms: float


class EngineStatsOut(BaseModel):
    """Engine operational metrics schema."""

    total_documents: int
    total_unique_terms: int
    total_postings: int
    avg_doc_length: float
    memory_usage_mb: float
    uptime_seconds: float


class BenchmarkResultOut(BaseModel):
    """Benchmark comparing AeroSearch Inverted Index vs Linear Scan."""

    query: str
    indexed_documents: int
    inverted_index_time_ms: float
    linear_scan_time_ms: float
    speedup_factor: float
    matches_found: int
