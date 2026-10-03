import React from "react";
import { Search, Sparkles } from "lucide-react";
import { AutocompleteItem } from "../types";

interface AutocompleteDropdownProps {
  suggestions: AutocompleteItem[];
  selectedIndex: number;
  onSelect: (term: string) => void;
  visible: boolean;
}

export const AutocompleteDropdown: React.FC<AutocompleteDropdownProps> = ({
  suggestions,
  selectedIndex,
  onSelect,
  visible,
}) => {
  if (!visible || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="absolute left-0 right-0 top-full mt-2 bg-slate-900/95 backdrop-blur-xl border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden z-50 transition-all">
      <div className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400 border-b border-slate-800/80 flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <Sparkles className="w-3 h-3 text-sky-400" />
          Trie Instant Suggestions
        </span>
        <span className="font-mono text-slate-500">Trie Prefix Match</span>
      </div>

      <ul className="py-1 divide-y divide-slate-800/40">
        {suggestions.map((item, index) => {
          const isSelected = index === selectedIndex;
          return (
            <li
              key={item.term}
              onMouseDown={(e) => {
                e.preventDefault();
                onSelect(item.term);
              }}
              className={`px-4 py-2.5 flex items-center justify-between cursor-pointer transition-colors ${
                isSelected
                  ? "bg-brand-600/20 text-brand-300 font-medium border-l-2 border-brand-500"
                  : "text-slate-300 hover:bg-slate-800/70 hover:text-white"
              }`}
            >
              <div className="flex items-center gap-3">
                <Search className={`w-4 h-4 ${isSelected ? "text-brand-400" : "text-slate-500"}`} />
                <span className="text-sm font-mono">{item.term}</span>
              </div>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                {item.frequency}x
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
};
