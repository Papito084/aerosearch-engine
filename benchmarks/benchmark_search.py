"""AeroSearch Performance Benchmark Suite.

Evaluates latency and throughput of:
1. AeroSearch BM25 Inverted Index vs Naive Linear Scan O(N)
2. Trie Autocomplete Prefix Search
3. Trie-guided Levenshtein Fuzzy Correction
"""

import statistics
import time

from aerosearch.core.engine import AeroSearchEngine
from aerosearch.data.generator import generate_demo_documents


def run_benchmark(corpus_size: int = 5000, runs: int = 15) -> None:
    print("=" * 80)
    print(f" AEROCORP / AEROSEARCH BENCHMARK SUITE (Corpus Size: {corpus_size:,} Documents)")
    print("=" * 80)

    # 1. Dataset Generation and Ingestion
    t_gen_start = time.perf_counter()
    docs = generate_demo_documents(count=corpus_size, seed=42)
    t_gen = time.perf_counter() - t_gen_start
    print(f"[*] Synthetic dataset generated in {t_gen * 1000:.2f} ms")

    engine = AeroSearchEngine(languages=["en", "es"])
    t_idx_start = time.perf_counter()
    engine.index_documents(docs)
    t_idx = time.perf_counter() - t_idx_start
    stats = engine.get_stats()
    throughput = corpus_size / t_idx
    print(
        f"[*] Indexed {stats.total_documents:,} docs ({stats.total_unique_terms:,} unique terms, "
        f"{stats.total_postings:,} postings) in {t_idx:.3f} s ({throughput:,.0f} docs/sec)"
    )
    print(f"[*] Memory RSS: {stats.memory_usage_mb:.2f} MB | Avg Doc Length: {stats.avg_doc_length:.1f} tokens\n")

    test_queries = [
        ("Single Term (Rare)", "hypersonic"),
        ("Single Term (Common)", "systems"),
        ("Multi-Term Conjunctive", "distributed consensus raft"),
        ("Complex Technical Query", "propulsion boundary layer shockwave"),
        ("Cross-Domain Query", "neural language model navigation"),
    ]

    print(f"{'Query Scenario':<32} | {'AeroSearch (ms)':<16} | {'Linear Scan (ms)':<16} | {'Speedup':<10}")
    print("-" * 80)

    all_speedups = []

    for label, query in test_queries:
        # Benchmark AeroSearch BM25
        aero_times = []
        for _ in range(runs):
            t0 = time.perf_counter_ns()
            res = engine.search(query, limit=10)
            t1 = time.perf_counter_ns()
            aero_times.append((t1 - t0) / 1_000_000.0)
        aero_median = statistics.median(aero_times)

        # Benchmark Linear Scan O(N)
        linear_times = []
        q_lower = query.lower()
        terms = q_lower.split()
        for _ in range(runs):
            t0 = time.perf_counter_ns()
            matches = 0
            for doc in docs:
                txt = (doc.title + " " + doc.content).lower()
                if any(t in txt for t in terms):
                    matches += 1
            t1 = time.perf_counter_ns()
            linear_times.append((t1 - t0) / 1_000_000.0)
        linear_median = statistics.median(linear_times)

        speedup = linear_median / max(aero_median, 0.0001)
        all_speedups.append(speedup)

        print(
            f"{label:<32} | {aero_median:>12.3f} ms | {linear_median:>12.3f} ms | {speedup:>8.1f}x"
        )

    avg_speedup = statistics.mean(all_speedups)
    print("-" * 80)
    print(f"[*] Mean Latency Reduction: {avg_speedup:.1f}x faster than Linear Scan\n")

    # 3. Trie Autocomplete Benchmark
    print("=" * 80)
    print(" TRIE PREFIX AUTOCOMPLETE LATENCY (Search-As-You-Type)")
    print("=" * 80)
    prefixes = ["a", "ae", "aero", "pro", "prop", "dist", "con", "hyp"]
    for p in prefixes:
        auto_times = []
        for _ in range(50):
            t0 = time.perf_counter_ns()
            auto_res = engine.autocomplete(p, limit=8)
            t1 = time.perf_counter_ns()
            auto_times.append((t1 - t0) / 1000.0)  # microseconds
        median_us = statistics.median(auto_times)
        matches = [item.term for item in auto_res.suggestions[:3]]
        print(f"Prefix '{p:<6}' -> {median_us:>7.2f} us ({len(auto_res.suggestions)} suggestions: {matches})")

    # 4. Fuzzy Levenshtein Correction Benchmark
    print("\n" + "=" * 80)
    print(" TRIE-GUIDED LEVENSHTEIN FUZZY CORRECTION ('Did you mean?')")
    print("=" * 80)
    typos = ["hipersonic", "propulsn", "consensuss", "algoritm", "paxoss"]
    for typo in typos:
        fuz_times = []
        correction = None
        for _ in range(50):
            t0 = time.perf_counter_ns()
            correction = engine.fuzzy_matcher.suggest_correction(typo, max_distance=2)
            t1 = time.perf_counter_ns()
            fuz_times.append((t1 - t0) / 1000.0)
        median_us = statistics.median(fuz_times)
        print(f"Typo '{typo:<12}' -> '{correction:<12}' resolved in {median_us:>7.2f} us")

    print("\n" + "=" * 80)
    print(" BENCHMARK COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark(corpus_size=5000)
