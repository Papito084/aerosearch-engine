"""FastAPI application entrypoint for AeroSearch."""

import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aerosearch.api.routes import router
from aerosearch.core.engine import AeroSearchEngine
from aerosearch.data.generator import generate_demo_documents

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aerosearch")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager initializing engine and loading demo documents."""
    logger.info("Initializing AeroSearch Core Engine...")
    engine = AeroSearchEngine(
        languages=["en", "es"],
        enable_stemming=True,
        enable_stopwords=True,
        bm25_k1=1.2,
        bm25_b=0.75,
    )
    app.state.engine = engine

    # Pre-index demo dataset
    demo_count = 5000
    logger.info(f"Generating and indexing {demo_count} demo documents...")
    t0 = time.perf_counter()
    demo_docs = generate_demo_documents(count=demo_count)
    indexed = engine.index_documents(demo_docs)
    elapsed = time.perf_counter() - t0
    logger.info(
        f"Indexed {indexed} documents in {elapsed:.3f}s. "
        f"Unique vocabulary: {engine.index.total_unique_terms} terms. Engine ready."
    )

    yield

    logger.info("Shutting down AeroSearch Engine.")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    application = FastAPI(
        title="AeroSearch Engine API",
        description="High-performance in-memory Full-Text Search Engine built from scratch.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS configuration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(router)

    @application.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "service": "aerosearch"}

    return application


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("aerosearch.api.main:app", host="0.0.0.0", port=8000, reload=True)
