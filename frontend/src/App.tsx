import React, { useState, useEffect, useCallback } from "react";
import { SearchBar } from "./components/SearchBar";
import { ResultCard } from "./components/ResultCard";
import { MetricsBar } from "./components/MetricsBar";
import { StatsModal } from "./components/StatsModal";
import { BenchmarkModal } from "./components/BenchmarkModal";
import { searchEngine, fetchEngineStats } from "./services/api";
import { SearchResponse, EngineStats } from "./types";
import { Rocket, ChevronLeft, ChevronRight, Compass } from "lucide-react";

export const App: React.FC = () => {
  const [query, setQuery] = useState("hypersonic");
  const [scoring, setScoring] = useState<"bm25" | "tfidf">("bm25");
  const [page, setPage] = useState(1);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [stats, setStats] = useState<EngineStats | null>(null);
  const [loading, setLoading] = useState(false);

  // Modals state
  const [isStatsOpen, setIsStatsOpen] = useState(false);
  const [isBenchmarkOpen, setIsBenchmarkOpen] = useState(false);

  // Load telemetry stats on mount
  useEffect(() => {
    fetchEngineStats()
      .then((data) => setStats(data))
      .catch((err) => console.error("Could not fetch stats:", err));
  }, []);

  // Perform search
  const executeSearch = useCallback(
    async (q: string, targetPage: number = 1, currentScoring: "bm25" | "tfidf" = scoring) => {
      const trimmed = q.trim();
      if (!trimmed) {
        setSearchResponse(null);
        return;
      }
      setLoading(true);
      try {
        const resp = await searchEngine(trimmed, targetPage, 10, currentScoring);
        setSearchResponse(resp);
        setPage(targetPage);
      } catch (err) {
        console.error("Search error:", err);
      } finally {
        setLoading(false);
      }
    },
    [scoring]
  );

  // Initial search on mount
  useEffect(() => {
    executeSearch("hypersonic", 1, scoring);
  }, []);

  const handleScoringChange = (newScoring: "bm25" | "tfidf") => {
    setScoring(newScoring);
    if (query.trim()) {
      executeSearch(query, 1, newScoring);
    }
  };

  const handleTagClick = (tag: string) => {
    setQuery(tag);
    executeSearch(tag, 1, scoring);
  };

  const quickPills = [
    "hypersonic",
    "distributed consensus",
    "ion propulsion",
    "boundary layer",
    "neural navigation",
    "inverted index",
    "paxos hotstuff",
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-brand-500 selection:text-white pb-16">
      {/* Top Banner / Navigation */}
      <header className="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl sticky top-0 z-40">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-brand-600 via-sky-500 to-indigo-500 p-0.5 shadow-lg shadow-brand-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                <Rocket className="w-5 h-5 text-brand-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-brand-400 bg-clip-text text-transparent">
                  AeroSearch
                </span>
                <span className="px-2 py-0.5 rounded-full bg-brand-950 text-brand-400 border border-brand-800/60 font-mono text-[10px] font-semibold">
                  v1.0 In-Memory
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Pure Algorithmic Full-Text Search Engine • BM25 • Trie • Levenshtein
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-slate-300 font-mono">
                {stats ? `${stats.total_documents.toLocaleString()} Docs` : "Connecting..."}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero & Search Section */}
      <main className="max-w-5xl mx-auto px-4 w-full flex flex-col gap-6 pt-8">
        {/* Search Bar */}
        <SearchBar
          query={query}
          onQueryChange={setQuery}
          onSearch={(q) => executeSearch(q, 1, scoring)}
          scoring={scoring}
          onScoringChange={handleScoringChange}
          didYouMean={searchResponse?.did_you_mean ?? null}
          isLoading={loading}
        />

        {/* Quick Search Chips */}
        <div className="flex items-center justify-center gap-2 flex-wrap text-xs text-slate-400">
          <span className="flex items-center gap-1 text-slate-500 font-medium">
            <Compass className="w-3.5 h-3.5" />
            Explore:
          </span>
          {quickPills.map((pill) => (
            <button
              key={pill}
              onClick={() => {
                setQuery(pill);
                executeSearch(pill, 1, scoring);
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800/80 font-mono text-[11px] transition"
            >
              {pill}
            </button>
          ))}
        </div>

        {/* Metrics Bar */}
        <MetricsBar
          executionTimeMs={searchResponse?.execution_time_ms ?? null}
          totalHits={searchResponse?.total_hits ?? null}
          stats={stats}
          onOpenStats={() => setIsStatsOpen(true)}
          onOpenBenchmark={() => setIsBenchmarkOpen(true)}
        />

        {/* Results Stream */}
        <div className="flex flex-col gap-4 mt-2">
          {searchResponse && searchResponse.results.length > 0 ? (
            searchResponse.results.map((item) => (
              <ResultCard
                key={item.doc_id}
                result={item}
                scoring={scoring}
                onTagClick={handleTagClick}
              />
            ))
          ) : !loading && query.trim() ? (
            <div className="text-center py-16 px-4 bg-slate-900/40 rounded-3xl border border-slate-800/80 flex flex-col items-center gap-3">
              <Compass className="w-10 h-10 text-slate-600" />
              <h4 className="text-lg font-semibold text-slate-200">No exact matches found</h4>
              <p className="text-sm text-slate-400 max-w-md">
                Try searching for broader engineering terms or check the fuzzy spelling suggestion above.
              </p>
            </div>
          ) : null}
        </div>

        {/* Pagination Controls */}
        {searchResponse && searchResponse.total_pages > 1 && (
          <div className="flex items-center justify-center gap-3 pt-6 pb-8">
            <button
              onClick={() => executeSearch(query, page - 1, scoring)}
              disabled={page <= 1}
              className="flex items-center gap-1 px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-40 disabled:hover:bg-slate-900 text-slate-300 border border-slate-800 transition text-sm font-medium"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>

            <span className="text-xs font-mono text-slate-400 px-3">
              Page <strong className="text-white">{page}</strong> of{" "}
              <strong className="text-white">{searchResponse.total_pages}</strong>
            </span>

            <button
              onClick={() => executeSearch(query, page + 1, scoring)}
              disabled={page >= searchResponse.total_pages}
              className="flex items-center gap-1 px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-40 disabled:hover:bg-slate-900 text-slate-300 border border-slate-800 transition text-sm font-medium"
            >
              <span>Next</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </main>

      {/* Diagnostics and Benchmark Modals */}
      <StatsModal
        stats={stats}
        isOpen={isStatsOpen}
        onClose={() => setIsStatsOpen(false)}
      />
      <BenchmarkModal
        isOpen={isBenchmarkOpen}
        onClose={() => setIsBenchmarkOpen(false)}
        initialQuery={query}
      />
    </div>
  );
};
