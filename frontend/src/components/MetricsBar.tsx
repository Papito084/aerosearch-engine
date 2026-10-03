import React from "react";
import { Zap, Clock, Database, BarChart3, Activity } from "lucide-react";
import { EngineStats } from "../types";

interface MetricsBarProps {
  executionTimeMs: number | null;
  totalHits: number | null;
  stats: EngineStats | null;
  onOpenStats: () => void;
  onOpenBenchmark: () => void;
}

export const MetricsBar: React.FC<MetricsBarProps> = ({
  executionTimeMs,
  totalHits,
  stats,
  onOpenStats,
  onOpenBenchmark,
}) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4 py-3 px-4 bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-xl text-xs text-slate-400 shadow-sm">
      <div className="flex items-center gap-6 flex-wrap">
        {executionTimeMs !== null && (
          <div className="flex items-center gap-1.5 text-emerald-400 font-mono font-medium">
            <Zap className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span>Resolved in {executionTimeMs.toFixed(2)} ms</span>
          </div>
        )}

        {totalHits !== null && (
          <div className="flex items-center gap-1.5 text-slate-300">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>
              <strong className="text-white font-semibold">{totalHits.toLocaleString()}</strong> matches
            </span>
          </div>
        )}

        {stats && (
          <>
            <div className="hidden sm:flex items-center gap-1.5 text-slate-400 border-l border-slate-800 pl-4">
              <Database className="w-3.5 h-3.5 text-sky-400" />
              <span>
                <strong className="text-slate-200">{stats.total_documents.toLocaleString()}</strong> docs indexed
              </span>
            </div>

            <div className="hidden md:flex items-center gap-1.5 text-slate-400">
              <Activity className="w-3.5 h-3.5 text-purple-400" />
              <span>
                RAM: <strong className="text-slate-200">{stats.memory_usage_mb} MB</strong>
              </span>
            </div>
          </>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onOpenBenchmark}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-sky-950/60 text-sky-300 hover:bg-sky-900/60 hover:text-sky-200 border border-sky-800/50 transition font-medium"
          title="Run live benchmark comparing Inverted Index vs Linear Scan"
        >
          <BarChart3 className="w-3.5 h-3.5 text-sky-400" />
          <span>Live Benchmark</span>
        </button>

        <button
          onClick={onOpenStats}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-700/60 transition font-medium"
          title="Inspect Engine Data Structures & Telemetry"
        >
          <Database className="w-3.5 h-3.5 text-slate-400" />
          <span>Engine Telemetry</span>
        </button>
      </div>
    </div>
  );
};
