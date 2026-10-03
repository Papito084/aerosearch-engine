import React, { useState, useEffect, useRef } from "react";
import { Search, X, Loader2, Sparkles, SlidersHorizontal } from "lucide-react";
import { AutocompleteDropdown } from "./AutocompleteDropdown";
import { autocompleteQuery } from "../services/api";
import { AutocompleteItem } from "../types";

interface SearchBarProps {
  query: string;
  onQueryChange: (q: string) => void;
  onSearch: (q: string) => void;
  scoring: "bm25" | "tfidf";
  onScoringChange: (s: "bm25" | "tfidf") => void;
  didYouMean: string | null;
  isLoading: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  onQueryChange,
  onSearch,
  scoring,
  onScoringChange,
  didYouMean,
  isLoading,
}) => {
  const [suggestions, setSuggestions] = useState<AutocompleteItem[]>([]);
  const [dropdownVisible, setDropdownVisible] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);


  // Debounce autocomplete prefix lookup
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    const trimmed = query.trim();
    if (!trimmed) {
      setSuggestions([]);
      setDropdownVisible(false);
      return;
    }

    // Extract the last word for multi-word queries to suggest completion on current word
    const words = trimmed.split(/\s+/);
    const lastWord = words[words.length - 1];

    if (lastWord.length < 1) {
      setSuggestions([]);
      setDropdownVisible(false);
      return;
    }

    debounceTimerRef.current = setTimeout(async () => {
      try {
        const resp = await autocompleteQuery(lastWord, 8);
        setSuggestions(resp.suggestions);
        setDropdownVisible(resp.suggestions.length > 0);
        setSelectedIndex(-1);
      } catch (err) {
        console.error("Autocomplete error:", err);
      }
    }, 120);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") {
      if (!dropdownVisible || suggestions.length === 0) return;
      e.preventDefault();
      setSelectedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      if (!dropdownVisible || suggestions.length === 0) return;
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (dropdownVisible && selectedIndex >= 0 && selectedIndex < suggestions.length) {
        handleSelectSuggestion(suggestions[selectedIndex].term);
      } else {
        setDropdownVisible(false);
        onSearch(query);
      }
    } else if (e.key === "Escape") {
      setDropdownVisible(false);
    }
  };

  const handleSelectSuggestion = (selectedTerm: string) => {
    const words = query.trim().split(/\s+/);
    if (words.length > 1) {
      words[words.length - 1] = selectedTerm;
      const newQuery = words.join(" ");
      onQueryChange(newQuery);
      onSearch(newQuery);
    } else {
      onQueryChange(selectedTerm);
      onSearch(selectedTerm);
    }
    setDropdownVisible(false);
  };

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col gap-3">
      {/* Search Input Box */}
      <div className="relative group">
        <div className="absolute inset-0 bg-gradient-to-r from-brand-500/20 via-sky-500/20 to-purple-500/20 rounded-2xl blur-xl opacity-50 group-focus-within:opacity-100 transition duration-300 pointer-events-none" />

        <div className="relative flex items-center bg-slate-900/90 backdrop-blur-xl border border-slate-700/80 rounded-2xl shadow-2xl focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-500/30 transition-all">
          <div className="pl-5 text-slate-400">
            {isLoading ? (
              <Loader2 className="w-6 h-6 animate-spin text-brand-400" />
            ) : (
              <Search className="w-6 h-6 text-slate-400 group-focus-within:text-brand-400 transition-colors" />
            )}
          </div>

          <input
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => {
              if (suggestions.length > 0) setDropdownVisible(true);
            }}
            placeholder="Search 5,000+ docs (e.g. 'hypersonic boundary', 'raft consensus', 'propulsion')..."
            className="w-full py-4 px-4 bg-transparent text-slate-100 text-lg placeholder-slate-500 focus:outline-none"
            autoFocus
          />

          <div className="flex items-center gap-2 pr-4">
            {query && (
              <button
                onClick={() => {
                  onQueryChange("");
                  setSuggestions([]);
                  setDropdownVisible(false);
                }}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                title="Clear query"
              >
                <X className="w-4 h-4" />
              </button>
            )}

            {/* Relevance model switcher */}
            <div className="hidden sm:flex items-center gap-1 bg-slate-950/60 p-1 rounded-lg border border-slate-800 text-xs">
              <SlidersHorizontal className="w-3.5 h-3.5 text-slate-400 ml-1" />
              <button
                type="button"
                onClick={() => onScoringChange("bm25")}
                className={`px-2 py-0.5 rounded font-medium transition ${
                  scoring === "bm25"
                    ? "bg-brand-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                title="Okapi BM25 with length normalization and IDF smoothing"
              >
                BM25
              </button>
              <button
                type="button"
                onClick={() => onScoringChange("tfidf")}
                className={`px-2 py-0.5 rounded font-medium transition ${
                  scoring === "tfidf"
                    ? "bg-brand-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                title="Term Frequency - Inverse Document Frequency"
              >
                TF-IDF
              </button>
            </div>
          </div>
        </div>

        {/* Autocomplete Dropdown */}
        <AutocompleteDropdown
          suggestions={suggestions}
          selectedIndex={selectedIndex}
          onSelect={handleSelectSuggestion}
          visible={dropdownVisible}
        />
      </div>

      {/* "Did you mean?" Typo Suggestion Pill */}
      {didYouMean && (
        <div className="flex items-center gap-2 px-4 py-2 bg-amber-950/40 border border-amber-800/50 rounded-xl text-xs text-amber-200 animate-fadeIn">
          <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
          <span>Did you mean:</span>
          <button
            onClick={() => {
              onQueryChange(didYouMean);
              onSearch(didYouMean);
            }}
            className="font-bold underline text-amber-300 hover:text-amber-100 cursor-pointer"
          >
            {didYouMean}
          </button>
          <span className="text-amber-400/60 text-[10px] ml-auto font-mono">
            Trie Levenshtein Distance Match
          </span>
        </div>
      )}
    </div>
  );
};
