export interface SearchResultItem {
  doc_id: string;
  title: string;
  content: string;
  tags: string[];
  metadata: Record<string, any>;
  score: number;
  highlight: string;
  matched_terms: string[];
}

export interface SearchResponse {
  query: string;
  total_hits: number;
  page: number;
  limit: number;
  total_pages: number;
  execution_time_ms: number;
  results: SearchResultItem[];
  did_you_mean: string | null;
}

export interface AutocompleteItem {
  term: string;
  frequency: number;
}

export interface AutocompleteResponse {
  prefix: string;
  suggestions: AutocompleteItem[];
  execution_time_ms: number;
}

export interface EngineStats {
  total_documents: number;
  total_unique_terms: number;
  total_postings: number;
  avg_doc_length: number;
  memory_usage_mb: number;
  uptime_seconds: number;
}

export interface BenchmarkResult {
  query: string;
  indexed_documents: number;
  inverted_index_time_ms: number;
  linear_scan_time_ms: number;
  speedup_factor: number;
  matches_found: number;
}
