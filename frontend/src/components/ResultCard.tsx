import React from "react";
import { SearchResultItem } from "../types";
import { Tag, User, Star, Eye, Calendar } from "lucide-react";

interface ResultCardProps {
  result: SearchResultItem;
  scoring: "bm25" | "tfidf";
  onTagClick: (tag: string) => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({
  result,
  scoring,
  onTagClick,
}) => {
  return (
    <article className="group p-5 bg-slate-900/70 hover:bg-slate-900/95 border border-slate-800 hover:border-slate-700 rounded-2xl shadow-lg transition-all duration-200 flex flex-col gap-3">
      {/* Header: Title and Relevancy Score Badge */}
      <div className="flex items-start justify-between gap-4">
        <h3 className="text-lg font-semibold text-slate-100 group-hover:text-brand-300 transition-colors leading-snug">
          {result.title}
        </h3>
        <div className="shrink-0 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-brand-950/80 border border-brand-800/60 text-brand-300 font-mono text-xs shadow-inner">
          <span className="text-[10px] text-brand-400 font-sans uppercase font-bold tracking-wider">
            {scoring.toUpperCase()}
          </span>
          <span className="font-semibold">{result.score.toFixed(3)}</span>
        </div>
      </div>

      {/* Highlighted Snippet */}
      <p
        className="text-sm text-slate-300 leading-relaxed font-sans"
        dangerouslySetInnerHTML={{ __html: result.highlight }}
      />

      {/* Metadata & Tags Footer */}
      <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400">
        <div className="flex items-center gap-2 flex-wrap">
          {result.tags.map((tag) => (
            <button
              key={tag}
              onClick={() => onTagClick(tag)}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-800/80 hover:bg-slate-750 text-slate-300 hover:text-white transition font-mono text-[11px]"
            >
              <Tag className="w-3 h-3 text-brand-400" />
              <span>{tag}</span>
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4 text-slate-400 text-[11px]">
          {result.metadata?.author && (
            <span className="flex items-center gap-1">
              <User className="w-3 h-3 text-slate-500" />
              <span>{result.metadata.author}</span>
            </span>
          )}

          {result.metadata?.year && (
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3 text-slate-500" />
              <span>{result.metadata.year}</span>
            </span>
          )}

          {result.metadata?.views && (
            <span className="flex items-center gap-1">
              <Eye className="w-3 h-3 text-slate-500" />
              <span>{result.metadata.views.toLocaleString()}</span>
            </span>
          )}

          {result.metadata?.rating && (
            <span className="flex items-center gap-1 text-amber-400 font-medium">
              <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
              <span>{result.metadata.rating}</span>
            </span>
          )}
        </div>
      </div>
    </article>
  );
};
