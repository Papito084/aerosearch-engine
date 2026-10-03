"""Unit tests for thread-safety and RWLock under concurrent read/write access."""

import concurrent.futures
import time

from aerosearch.core.engine import AeroSearchEngine
from aerosearch.core.models import Document


def test_concurrent_readers_and_writers() -> None:
    engine = AeroSearchEngine()

    # Preload initial documents
    initial_docs = [
        Document(
            id=f"init-{i}",
            title=f"Initial Document {i} regarding propulsion",
            content=f"Detailed analysis of propulsion and aerodynamics system {i}.",
            tags=["aerospace"],
        )
        for i in range(50)
    ]
    engine.index_documents(initial_docs)

    num_readers = 8
    num_writers = 4
    iterations = 25

    errors: list[Exception] = []

    def reader_task() -> None:
        try:
            for _ in range(iterations):
                res = engine.search("propulsion", limit=5)
                assert res.total_hits > 0
                time.sleep(0.001)
        except Exception as e:
            errors.append(e)

    def writer_task(writer_id: int) -> None:
        try:
            for j in range(iterations):
                doc = Document(
                    id=f"concurrent-{writer_id}-{j}",
                    title=f"Concurrent Written Doc {writer_id}-{j}",
                    content="High frequency updates to inverted index under write lock.",
                    tags=["concurrency"],
                )
                engine.index_document(doc)
                time.sleep(0.001)
        except Exception as e:
            errors.append(e)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_readers + num_writers) as executor:
        futures = []
        for _ in range(num_readers):
            futures.append(executor.submit(reader_task))
        for w in range(num_writers):
            futures.append(executor.submit(writer_task, w))

        concurrent.futures.wait(futures)

    assert len(errors) == 0, f"Encountered concurrency errors: {errors}"
    stats = engine.get_stats()
    assert stats.total_documents == 50 + (num_writers * iterations)
