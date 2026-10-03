import React, { useState } from "react";
import { X, Play, Zap, BarChart3, CheckCircle2, Loader2 } from "lucide-react";
import { runQueryBenchmark } from "../services/api";
import { BenchmarkResult } from "../types";

interface BenchmarkModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialQuery?: string;
}

export const BenchmarkModal: React.FC<BenchmarkModalProps> = ({
  isOpen,
  onClose,
  initialQuery = "hypersonic",
}) => {
  const [benchQuery, setBenchQuery] = useState(initialQuery);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BenchmarkResult | null>(null);

  if (!isOpen) return null;

  const handleRun = async (qToRun?: string) => {
    const targetQ = qToRun || benchQuery;
    if (!targetQ.trim()) return;
    setLoading(true);
    try {
      const data = await runQueryBenchmark(targetQ.trim());
      setResult(data);
    } catch (err) {
      console.error("Benchmark failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-sky-600/20 text-sky-400">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Live Engine Benchmark</h2>
              <p className="text-xs text-slate-400">
                Inverted Index BM25 vs Linear Scan O(N) Substring Match
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 flex flex-col gap-6">
          {/* Query input and run button */}
          <div className="flex gap-2">
            <input
              type="text"
              value={benchQuery}
              onChange={(e) => setBenchQuery(e.target.value)}
              placeholder="Query to benchmark (e.g. 'propulsion', 'consensus')..."
              className="flex-1 py-2.5 px-4 bg-slate-950 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500 font-mono"
            />
            <button
              onClick={() => handleRun()}
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white font-medium text-sm rounded-xl transition shadow-lg shadow-brand-600/30"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4 fill-white" />
              )}
              <span>Run Benchmark</span>
            </button>
          </div>

          {/* Quick presets */}
          <div className="flex items-center gap-2 flex-wrap text-xs text-slate-400">
            <span>Quick presets:</span>
            {["hypersonic", "distributed consensus", "propulsion", "neural navigation"].map((preset) => (
              <button
                key={preset}
                onClick={() => {
                  setBenchQuery(preset);
                  handleRun(preset);
                }}
                className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-750 text-slate-300 font-mono hover:text-white transition"
              >
                {preset}
              </button>
            ))}
          </div>

          {/* Results Display */}
          {result && (
            <div className="flex flex-col gap-5 p-5 rounded-2xl bg-slate-950 border border-slate-800">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <span className="text-xs text-slate-400 font-mono">
                  Target Corpus: <strong className="text-white">{result.indexed_documents.toLocaleString()}</strong> docs
                </span>
                <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-bold font-mono">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  Speedup: {result.speedup_factor}x Faster
                </span>
              </div>

              {/* Latency comparison visual bars */}
              <div className="flex flex-col gap-4">
                {/* AeroSearch Bar */}
                <div className="flex flex-col gap-1.5">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="flex items-center gap-1.5 text-brand-300 font-semibold">
                      <Zap className="w-3.5 h-3.5 text-brand-400" />
                      AeroSearch BM25 Postings List
                    </span>
                    <span className="text-brand-300 font-bold">
                      {result.inverted_index_time_ms.toFixed(3)} ms
                    </span>
                  </div>
                  <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-brand-500 to-sky-400 rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.max(
                          4,
                          (result.inverted_index_time_ms /
                            Math.max(result.linear_scan_time_ms, 0.001)) *
                            100
                        )}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Linear Scan Bar */}
                <div className="flex flex-col gap-1.5">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-400">Linear Scan Baseline (O(N))</span>
                    <span className="text-slate-300 font-bold">
                      {result.linear_scan_time_ms.toFixed(3)} ms
                    </span>
                  </div>
                  <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-slate-600 rounded-full w-full" />
                  </div>
                </div>
              </div>

              <div className="pt-2 text-[11px] text-slate-500 font-mono">
                Formula verified: BM25 score computed on candidate postings intersection in {result.inverted_index_time_ms.toFixed(3)} ms vs complete sequential document substring scanning in {result.linear_scan_time_ms.toFixed(3)} ms.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
