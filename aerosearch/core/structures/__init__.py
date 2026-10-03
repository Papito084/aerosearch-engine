"""Data structures for AeroSearch."""

from aerosearch.core.structures.fuzzy import (
    TrieFuzzyMatcher,
    damerau_levenshtein_distance,
    levenshtein_distance,
)
from aerosearch.core.structures.inverted_index import InvertedIndex
from aerosearch.core.structures.rwlock import RWLock
from aerosearch.core.structures.trie import Trie, TrieNode

__all__ = [
    "InvertedIndex",
    "RWLock",
    "Trie",
    "TrieFuzzyMatcher",
    "TrieNode",
    "damerau_levenshtein_distance",
    "levenshtein_distance",
]
