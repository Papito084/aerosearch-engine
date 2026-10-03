import {
  AutocompleteResponse,
  BenchmarkResult,
  EngineStats,
  SearchResponse,
} from "../types";

const API_BASE = "/api/v1";

export async function searchEngine(
  query: string,
  page: number = 1,
  limit: number = 10,
  scoring: "bm25" | "tfidf" = "bm25"
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    page: page.toString(),
    limit: limit.toString(),
    scoring,
  });

  const res = await fetch(`${API_BASE}/search?${params.toString()}`);
  if (!res.ok) {
    throw new Error(`Search failed: ${res.statusText}`);
  }
  return res.json();
}

export async function autocompleteQuery(
  prefix: string,
  limit: number = 8
): Promise<AutocompleteResponse> {
  if (!prefix.trim()) {
    return { prefix: "", suggestions: [], execution_time_ms: 0 };
  }

  const params = new URLSearchParams({
    prefix,
    limit: limit.toString(),
  });

  const res = await fetch(`${API_BASE}/autocomplete?${params.toString()}`);
  if (!res.ok) {
    throw new Error(`Autocomplete failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchEngineStats(): Promise<EngineStats> {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) {
    throw new Error(`Failed to load engine statistics: ${res.statusText}`);
  }
  return res.json();
}

export async function runQueryBenchmark(query: string): Promise<BenchmarkResult> {
  const params = new URLSearchParams({ q: query });
  const res = await fetch(`${API_BASE}/benchmark?${params.toString()}`);
  if (!res.ok) {
    throw new Error(`Benchmark failed: ${res.statusText}`);
  }
  return res.json();
}
