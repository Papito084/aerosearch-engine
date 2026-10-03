import React from "react";
import { X, Database, Cpu, Layers, HardDrive, Clock, FileText } from "lucide-react";
import { EngineStats } from "../types";

interface StatsModalProps {
  stats: EngineStats | null;
  onClose: () => void;
  isOpen: boolean;
}

export const StatsModal: React.FC<StatsModalProps> = ({ stats, onClose, isOpen }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-xl bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-brand-600/20 text-brand-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Engine Telemetry & Memory</h2>
              <p className="text-xs text-slate-400">Real-time internal data structures diagnostics</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 flex flex-col gap-6">
          {stats ? (
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 flex flex-col gap-1">
                <span className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                  <FileText className="w-4 h-4 text-sky-400" />
                  Indexed Documents
                </span>
                <span className="text-2xl font-bold font-mono text-white">
                  {stats.total_documents.toLocaleString()}
                </span>
                <span className="text-[11px] text-slate-500">In-memory documents corpus</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 flex flex-col gap-1">
                <span className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                  <Layers className="w-4 h-4 text-purple-400" />
                  Unique Vocabulary
                </span>
                <span className="text-2xl font-bold font-mono text-white">
                  {stats.total_unique_terms.toLocaleString()}
                </span>
                <span className="text-[11px] text-slate-500">Distinct stemmed roots</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 flex flex-col gap-1">
                <span className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                  <HardDrive className="w-4 h-4 text-emerald-400" />
                  Postings Entries
                </span>
                <span className="text-2xl font-bold font-mono text-white">
                  {stats.total_postings.toLocaleString()}
                </span>
                <span className="text-[11px] text-slate-500">Inverted index posting nodes</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 flex flex-col gap-1">
                <span className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                  <Cpu className="w-4 h-4 text-amber-400" />
                  RAM Consumption
                </span>
                <span className="text-2xl font-bold font-mono text-white">
                  {stats.memory_usage_mb.toFixed(1)} MB
                </span>
                <span className="text-[11px] text-slate-500">Resident Set Size (RSS)</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 flex flex-col gap-1">
                <span className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  Avg Document Length
                </span>
                <span className="text-2xl font-bold font-mono text-white">
                  {stats.avg_doc_length.toFixed(1)}
                </span>
                <span className="text-[11px] text-slate-500">Tokens per document (avgdl)</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 flex flex-col gap-1">
                <span className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                  <Clock className="w-4 h-4 text-rose-400" />
                  Engine Uptime
                </span>
                <span className="text-2xl font-bold font-mono text-white">
                  {Math.floor(stats.uptime_seconds)}s
                </span>
                <span className="text-[11px] text-slate-500">Elapsed process seconds</span>
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Telemetry metrics loading...</p>
          )}

          {/* Architecture Summary Box */}
          <div className="p-4 rounded-2xl bg-slate-950/90 border border-slate-800 text-xs text-slate-300 flex flex-col gap-2 font-mono">
            <div className="text-slate-400 font-bold uppercase tracking-wider text-[10px]">
              Engine Architecture Highlights
            </div>
            <ul className="list-disc pl-4 space-y-1 text-slate-400">
              <li>Lock-free / RWLock concurrent read-write guarantees.</li>
              <li>Trie-guided Levenshtein branch-and-bound pruning.</li>
              <li>Robertson-Spärck Jones smoothed Okapi BM25 ranking.</li>
              <li>Zero external database or C++ dependencies.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
