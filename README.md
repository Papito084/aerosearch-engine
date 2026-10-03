# AeroSearch 🚀

> **High-Performance In-Memory Full-Text Search Engine built from scratch in Python 3.12.**  
> *Zero external databases. Zero off-the-shelf retrieval packages (No Lucene, No Elasticsearch, No Whoosh).*  
> *Strict Python typing (Mypy 100%), pure algorithmic data structures, >90% test coverage, and modern React 18 frontend.*

---

## 📑 Table of Contents
1. [Architectural Overview](#-architectural-overview)
2. [Algorithmic Core & Data Structures](#-algorithmic-core--data-structures)
3. [Mathematical Foundations & Formulas](#-mathematical-foundations--formulas)
   - [Okapi BM25 Ranking with Robertson Smoothing](#1-okapi-bm25-ranking)
   - [Damerau-Levenshtein & Trie Branch-and-Bound](#2-levenshtein--trie-automaton)
4. [Performance Benchmarks](#-performance-benchmarks)
5. [API Specification (FastAPI)](#-api-specification)
6. [Interactive Frontend Interface](#-interactive-frontend-interface)
7. [Installation & Deployment](#-installation--deployment)
   - [Docker Compose (Single Command)](#docker-compose-production)
   - [Local Development Setup](#local-development)
8. [Testing & Quality Verification](#-testing--quality-verification)

---

## 🏛 Architectural Overview

AeroSearch is engineered under **Clean Architecture** principles, decoupling text analysis, internal memory layouts, ranking heuristics, and HTTP serving:

```mermaid
flowchart TD
    subgraph ClientLayer["Frontend & Client Layer"]
        UI["React 18 + TS + Tailwind (Port 3000)"]
        API_Call["REST Client (Debounced 120ms)"]
        UI --> API_Call
    end

    subgraph ServiceLayer["Service & Concurrency Layer (Port 8000)"]
        FastAPI["FastAPI Async Framework"]
        RWLock["Fair RWLock (threading.Condition)"]
        API_Call --> FastAPI
        FastAPI --> RWLock
    end

    subgraph EngineCore["AeroSearch Core Engine (In-Memory)"]
        subgraph Pipeline["Ingestion & Analysis Pipeline"]
            Norm["Unicode Normalizer (NFKD Accent Stripping)"]
            Stop["Stop-Words Filter (EN / ES)"]
            Stem["Porter Stemmer (Porter 1980 + LRU Cache)"]
            Norm --> Stop --> Stem
        end

        subgraph MemoryStructures["In-Memory Data Structures"]
            InvIndex["Inverted Index\n(Term -> Postings: doc_id, tf, positions)"]
            Trie["Prefix Tree (Trie)\n(Frequency-Ranked Autocomplete)"]
            FuzzyMatcher["Trie Levenshtein Fuzzy Matcher\n(Pruned Branch-and-Bound)"]
        end

        subgraph ScoringEngine["Relevance & Snippet Engine"]
            BM25["Okapi BM25 Scorer\n(k1=1.2, b=0.75, Smoothed IDF)"]
            Highlighter["Density Window Hit Highlighter\n(<mark> Tagging)"]
        end
    end

    RWLock --> Pipeline
    Pipeline --> MemoryStructures
    MemoryStructures --> ScoringEngine
    ScoringEngine --> FastAPI
```

### Concurrency Model (Reader-Writer Lock)

To achieve maximum throughput under mixed read/write workloads, AeroSearch implements a fair **Reader-Writer Lock (`RWLock`)**:
- **Concurrent Readers**: Multiple search threads query the Inverted Index and Trie simultaneously without acquiring exclusive locks.
- **Exclusive Writers**: When new documents are indexed (`POST /api/v1/index/documents`), write transactions obtain exclusive access.
- **Writer-Starvation Prevention**: Queued writers signal upcoming exclusivity, preventing endless reader streams from delaying writes.

```mermaid
sequenceDiagram
    autonumber
    actor Reader1 as Search Worker 1
    actor Reader2 as Search Worker 2
    actor Writer as Index Ingestion Worker
    participant RW as Fair RWLock
    participant Index as Inverted Index

    Reader1->>RW: acquire_read()
    RW-->>Reader1: Grant Read Lock (readers=1)
    Reader2->>RW: acquire_read()
    RW-->>Reader2: Grant Read Lock (readers=2)
    Writer->>RW: acquire_write()
    Note over RW: Active readers exist (readers=2). Writer waits.
    Reader1->>Index: Read Postings List (BM25)
    Reader2->>Index: Read Postings List (BM25)
    Reader1->>RW: release_read() (readers=1)
    Reader2->>RW: release_read() (readers=0)
    RW-->>Writer: Grant Exclusive Write Lock (active=True)
    Writer->>Index: Atomic Batch Insertion
    Writer->>RW: release_write()
    Note over RW: Unblocks subsequent queued operations
```

---

## 🧩 Algorithmic Core & Data Structures

### 1. Inverted Index (`InvertedIndex`)
Maps stemmed vocabulary tokens to dynamic posting lists. Each posting node tracks:
- `doc_id`: Unique identifier of the document.
- `term_frequency` ($f(q, D)$): Total occurrences of the term in document $D$.
- `positions`: Integer array of token offsets for phrase matching and hit highlighting.
- Constant time $O(1)$ addition, removal, and document length tracking ($|D|$, $\text{avgdl}$).

### 2. Prefix Tree (`Trie`)
- Each node stores outgoing character edges, terminal flags, complete words, and corpus frequencies.
- **Search-As-You-Type**: Given prefix $P$, walks down $|P|$ nodes. Subtree extraction utilizes a **bounded min-heap** maintaining top $K$ suggestions in $O(M \log K)$ where $M$ is subtree cardinality. Typical autocomplete response: **3 to 25 microseconds**.

### 3. Trie-Guided Levenshtein Automaton (`TrieFuzzyMatcher`)
Instead of calculating Levenshtein distance sequentially across $V$ vocabulary words ($O(V \cdot N \cdot M)$), AeroSearch combines the Trie with **recursive dynamic programming branch-and-bound**:
- Initial row vector is $[0, 1, 2, \dots, |target|]$.
- As the search descends into Trie edge char $c$, the next Levenshtein row is computed in $O(|target|)$.
- If $\min(\text{row}) > \text{max\_distance}$ (typically $2$), the **entire subtree is pruned immediately**.
- Typo suggestions ("Did you mean?") resolve in **sub-millisecond (< 1.2 ms)** time over 10,000+ words.

---

## 📐 Mathematical Foundations & Formulas

### 1. Okapi BM25 Ranking

Given document $D$ and query $Q = \{q_1, q_2, \dots, q_n\}$, the BM25 score is computed as:

$$\text{Score}(D, Q) = \sum_{i=1}^n \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$

Where:
- $f(q_i, D)$ is the term frequency of $q_i$ in document $D$.
- $|D|$ is the length of document $D$ in tokens.
- $\text{avgdl}$ is the average document length across the entire corpus:
  $$\text{avgdl} = \frac{1}{N} \sum_{k=1}^N |D_k|$$
- $k_1 = 1.2$ controls term frequency saturation.
- $b = 0.75$ controls document length normalization penalty.

#### Robertson-Spärck Jones Smoothed IDF
To prevent negative scores when a term occurs in more than half of the corpus ($n(q_i) > N/2$), AeroSearch implements the lower-bounded smoothed formula:

$$\text{IDF}(q_i) = \ln\left(1 + \frac{N - n(q_i) + 0.5}{n(q_i) + 0.5}\right)$$

Where:
- $N$ is total documents indexed.
- $n(q_i)$ is the number of documents containing term $q_i$.

---

### 2. Levenshtein & Trie Automaton

The edit distance between strings $s_1$ and $s_2$ is defined recursively by the Wagner-Fischer dynamic programming matrix:

$$D(i, j) = \begin{cases} 
\max(i, j) & \text{if } \min(i, j) = 0, \\
\min \begin{cases} 
D(i-1, j) + 1 \\ 
D(i, j-1) + 1 \\ 
D(i-1, j-1) + \mathbb{I}(s_1[i] \neq s_2[j]) 
\end{cases} & \text{otherwise.}
\end{cases}$$

For Damerau-Levenshtein, transposition cost is evaluated when $i, j > 1$ and $s_1[i] = s_2[j-1]$ and $s_1[i-1] = s_2[j]$:

$$D(i, j) = \min(D(i, j), D(i-2, j-2) + 1)$$

---

## ⚡ Performance Benchmarks

The benchmark suite (`benchmarks/benchmark_search.py`) evaluates query execution latency on a preloaded corpus of **5,000 documents** (~344,000 indexed postings) comparing **AeroSearch Inverted Index BM25** against a **Linear Scan ($O(N)$ Substring Search)**:

| Query Scenario | Query Terms | AeroSearch BM25 (ms) | Linear Scan $O(N)$ (ms) | Speedup Factor |
| :--- | :--- | :---: | :---: | :---: |
| **Single Term (Rare)** | `hypersonic` | **0.434 ms** | 3.755 ms | **8.6x** |
| **Single Term (Common)** | `systems` | **0.775 ms** | 3.705 ms | **4.8x** |
| **Multi-Term Conjunctive** | `distributed consensus raft` | **0.936 ms** | 6.403 ms | **6.8x** |
| **Complex Technical Query** | `propulsion boundary layer shockwave` | **1.642 ms** | 7.187 ms | **4.4x** |
| **Cross-Domain Query** | `neural language model navigation` | **1.578 ms** | 8.082 ms | **5.1x** |

### Micro-Benchmark: Trie Operations & Fuzzy Correction

| Operation | Query / Input | Latency | Result / Output |
| :--- | :--- | :---: | :--- |
| **Prefix Autocomplete** | `aero` | **7.30 μs** | 4 ranked completions (`aerospace`, `aeronautics`, etc.) |
| **Prefix Autocomplete** | `prop` | **3.90 μs** | 1 completion (`propulsion`) |
| **Prefix Autocomplete** | `hyp` | **3.80 μs** | 1 completion (`hypersonic`) |
| **Typo Correction (dist=1)** | `hipersonic` | **1.26 ms** | `hypersonic` |
| **Typo Correction (dist=1)** | `propulsn` | **1.14 ms** | `propulsion` |
| **Typo Correction (dist=1)** | `algoritm` | **1.13 ms** | `algorithm` |

*Hardware: Intel Core i7 / AMD Ryzen (single-threaded measurement). Engine memory footprint: ~93 MB RSS.*

---

## 🌐 API Specification

FastAPI asynchronous API exposed at `http://localhost:8000`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/index/documents` | Ingest bulk or single document payload (`id`, `title`, `content`, `tags`, `metadata`). |
| `GET` | `/api/v1/search?q={query}&limit=10&page=1` | BM25 search with hit highlighting, pagination, and typo detection. |
| `GET` | `/api/v1/autocomplete?prefix={prefix}` | Real-time Trie prefix completion ordered by frequency. |
| `GET` | `/api/v1/stats` | In-memory engine telemetry: doc count, unique terms, postings, RAM usage. |
| `GET` | `/api/v1/benchmark?q={query}` | Real-time comparative benchmark vs Linear Scan $O(N)$. |
| `GET` | `/health` | Kubernetes/Docker healthcheck probe. |

### Sample Search Response (`GET /api/v1/search?q=hypersonic`)

```json
{
  "query": "hypersonic",
  "total_hits": 612,
  "page": 1,
  "limit": 10,
  "total_pages": 62,
  "execution_time_ms": 0.842,
  "results": [
    {
      "doc_id": "aero-doc-00042",
      "title": "Aerodynamics of Hypersonic Glider X-43: Boundary Layer Transition at Mach 5.8",
      "content": "Investigating shockwave boundary layer interactions on Hypersonic Glider X-43...",
      "tags": ["aerospace", "hypersonic"],
      "metadata": {
        "author": "Dr. Elena Vance",
        "category": "Aerospace & Aeronautics",
        "views": 18450,
        "rating": 4.9
      },
      "score": 4.2185,
      "highlight": "...shockwave boundary layer interactions on <mark class=\"bg-amber-200 text-amber-950 font-semibold px-1 py-0.5 rounded\">Hypersonic</mark> Glider X-43 during atmospheric flight...",
      "matched_terms": ["hypersonic"]
    }
  ],
  "did_you_mean": null
}
```

---

## 💻 Interactive Frontend Interface

The frontend (`/frontend`) is built with **React 18 + TypeScript + Vite + Tailwind CSS**:
- **Raycast/Google Search Bar**: Real-time debounce (120ms) querying the in-memory Trie with keyboard navigation (`↑`, `↓`, `Enter`, `Esc`).
- **Telemetry Header**: Displays real-time resolution latency in microseconds/milliseconds (e.g. `Resolved in 0.84 ms`), match counter, and document counts.
- **BM25 Relevancy Badges & Snippet Highlighting**: Visual relevance score chips with density-centered `<mark>` matching.
- **"Did You Mean?" Typo Correction Pills**: Interactive suggestion banner when queries have minor misspellings.
- **Live Interactive Benchmark Modal**: Directly compare AeroSearch vs sequential scanning with live progress bars.

---

## 🚀 Installation & Deployment

### Docker Compose (Production)

To launch both the AeroSearch Engine and the Nginx Frontend in isolated containers with a single command:

```bash
docker compose up --build
```

- **Frontend Application**: `http://localhost:3000`
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`

---

### Local Development

#### 1. Backend Setup (Python 3.11+)

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # On Windows
# source venv/bin/activate     # On Linux / macOS

# Install package and dev dependencies
pip install -e .
pip install -r requirements-dev.txt

# Run the API server with 5,000 preloaded demo documents
uvicorn aerosearch.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup (Node 16+)

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` in your browser.

---

## 🧪 Testing & Quality Verification

Run the full suite of unit, concurrency, and mathematical verification tests:

```bash
# Execute Pytest test suite with code coverage
pytest --cov=aerosearch --cov-report=term-missing

# Strict code formatting and linting (Ruff)
ruff check aerosearch tests
ruff format --check aerosearch tests

# Static type verification (Mypy)
mypy aerosearch tests

# Run search latency benchmarks
python benchmarks/benchmark_search.py
```

### Verified Test Suite Breakdown (25 Tests)
- `test_tokenizer.py`: Normalization, accent stripping (NFKD), stop-words filtering, position tracking.
- `test_stemmer.py`: Porter Stemmer Steps 1a through 5b, plurals, suffixes, invariant caching.
- `test_trie.py`: Prefix insertions, subtree traversal, frequency-ranked autocomplete.
- `test_fuzzy.py`: Levenshtein dynamic programming, Damerau transposition, Trie branch-and-bound typo suggestion.
- `test_inverted_index.py`: Postings creation, document removals, index statistics.
- `test_bm25.py`: **Manual mathematical calculation verification** matching theoretical formulas with `pytest.approx`.
- `test_concurrency.py`: ThreadPoolExecutor with concurrent readers and writers under `RWLock`.
- `test_highlighter.py`: Density window snippet extraction, XSS sanitization, HTML tag safety.
- `test_api.py`: FastAPI endpoints integration via `httpx.AsyncClient`.

---

## 📄 License
MIT License. Built with algorithmic precision.
