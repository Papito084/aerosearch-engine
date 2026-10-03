"""FastAPI route handlers for AeroSearch."""

import time
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from aerosearch.api.schemas import (
    AutocompleteItemOut,
    AutocompleteResponseOut,
    BenchmarkResultOut,
    BulkIndexRequest,
    BulkIndexResponse,
    DocumentIn,
    EngineStatsOut,
    SearchResponseOut,
    SearchResultItemOut,
)
from aerosearch.core.engine import AeroSearchEngine
from aerosearch.core.models import Document

router = APIRouter(prefix="/api/v1", tags=["AeroSearch"])


def get_engine(request: Request) -> AeroSearchEngine:
    """Dependency that extracts the singleton engine from app state, initializing if necessary."""
    if not hasattr(request.app.state, "engine") or request.app.state.engine is None:
        request.app.state.engine = AeroSearchEngine(
            languages=["en", "es"],
            enable_stemming=True,
            enable_stopwords=True,
        )
    return request.app.state.engine  # type: ignore[no-any-return]


@router.post("/index/documents", response_model=BulkIndexResponse, status_code=201)
async def index_documents(
    payload: BulkIndexRequest | DocumentIn,
    engine: Annotated[AeroSearchEngine, Depends(get_engine)],
) -> BulkIndexResponse:
    """Index one or multiple documents into the in-memory engine."""
    if isinstance(payload, DocumentIn):
        docs_to_index = [
            Document(
                id=payload.id,
                title=payload.title,
                content=payload.content,
                tags=payload.tags,
                metadata=payload.metadata,
            )
        ]
    else:
        docs_to_index = [
            Document(
                id=d.id,
                title=d.title,
                content=d.content,
                tags=d.tags,
                metadata=d.metadata,
            )
            for d in payload.documents
        ]

    count = engine.index_documents(docs_to_index)
    return BulkIndexResponse(
        indexed_count=count,
        message=f"Successfully indexed {count} document(s).",
    )


@router.get("/search", response_model=SearchResponseOut)
async def search(
    q: Annotated[str, Query(description="Search query string", min_length=1)],
    engine: Annotated[AeroSearchEngine, Depends(get_engine)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    scoring: Annotated[str, Query(pattern="^(bm25|tfidf)$")] = "bm25",
) -> SearchResponseOut:
    """Execute full-text search with BM25/TF-IDF scoring and snippet highlighting."""
    resp = engine.search(query=q, page=page, limit=limit, scoring=scoring)
    return SearchResponseOut(
        query=resp.query,
        total_hits=resp.total_hits,
        page=resp.page,
        limit=resp.limit,
        total_pages=resp.total_pages,
        execution_time_ms=resp.execution_time_ms,
        results=[
            SearchResultItemOut(
                doc_id=r.doc_id,
                title=r.title,
                content=r.content,
                tags=r.tags,
                metadata=r.metadata,
                score=r.score,
                highlight=r.highlight,
                matched_terms=r.matched_terms,
            )
            for r in resp.results
        ],
        did_you_mean=resp.did_you_mean,
    )


@router.get("/autocomplete", response_model=AutocompleteResponseOut)
async def autocomplete(
    prefix: Annotated[str, Query(description="Query prefix for instant completion")],
    engine: Annotated[AeroSearchEngine, Depends(get_engine)],
    limit: Annotated[int, Query(ge=1, le=20)] = 8,
) -> AutocompleteResponseOut:
    """Instant search-as-you-type autocomplete suggestions from Trie."""
    resp = engine.autocomplete(prefix=prefix, limit=limit)
    return AutocompleteResponseOut(
        prefix=resp.prefix,
        suggestions=[
            AutocompleteItemOut(term=item.term, frequency=item.frequency)
            for item in resp.suggestions
        ],
        execution_time_ms=resp.execution_time_ms,
    )



@router.get("/stats", response_model=EngineStatsOut)
async def stats(
    engine: Annotated[AeroSearchEngine, Depends(get_engine)],
) -> EngineStatsOut:
    """Retrieve in-memory engine diagnostic and performance metrics."""
    s = engine.get_stats()
    return EngineStatsOut(
        total_documents=s.total_documents,
        total_unique_terms=s.total_unique_terms,
        total_postings=s.total_postings,
        avg_doc_length=s.avg_doc_length,
        memory_usage_mb=s.memory_usage_mb,
        uptime_seconds=s.uptime_seconds,
    )


@router.get("/benchmark", response_model=BenchmarkResultOut)
async def benchmark(
    q: Annotated[str, Query(description="Query to benchmark")],
    engine: Annotated[AeroSearchEngine, Depends(get_engine)],
) -> BenchmarkResultOut:
    """Benchmark comparing AeroSearch BM25 Inverted Index vs Linear O(N) Substring Scan."""
    query_str = q.strip().lower()

    # 1. AeroSearch Inverted Index BM25 search
    start_inv = time.perf_counter_ns()
    inv_resp = engine.search(query=query_str, limit=50)
    inv_time_ms = (time.perf_counter_ns() - start_inv) / 1_000_000.0

    # 2. Linear Scan Baseline (O(N) iteration through every document's text)
    with engine.rwlock.read_lock():
        all_doc_ids = engine.index.get_all_doc_ids()
        start_lin = time.perf_counter_ns()
        linear_matches = 0
        for doc_id in all_doc_ids:
            doc = engine.index.get_document(doc_id)
            if doc and (query_str in doc.title.lower() or query_str in doc.content.lower()):
                linear_matches += 1
        lin_time_ms = (time.perf_counter_ns() - start_lin) / 1_000_000.0

    speedup = round(lin_time_ms / max(inv_time_ms, 0.0001), 2)

    return BenchmarkResultOut(
        query=query_str,
        indexed_documents=len(all_doc_ids),
        inverted_index_time_ms=round(inv_time_ms, 3),
        linear_scan_time_ms=round(lin_time_ms, 3),
        speedup_factor=speedup,
        matches_found=inv_resp.total_hits,
    )
