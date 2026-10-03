"""Unit tests for Levenshtein, Damerau-Levenshtein, and TrieFuzzyMatcher."""

from aerosearch.core.structures.fuzzy import (
    TrieFuzzyMatcher,
    damerau_levenshtein_distance,
    levenshtein_distance,
)
from aerosearch.core.structures.trie import Trie


def test_levenshtein_distance() -> None:
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("aerosearch", "aerosearch") == 0
    assert levenshtein_distance("", "hello") == 5
    assert levenshtein_distance("algorithm", "algoritm") == 1


def test_damerau_levenshtein_transposition() -> None:
    # Transposition of adjacent characters is 1 edit in Damerau-Levenshtein, but 2 in Levenshtein
    assert damerau_levenshtein_distance("ca", "ac") == 1
    assert levenshtein_distance("ca", "ac") == 2


def test_trie_fuzzy_matcher_did_you_mean() -> None:
    trie = Trie()
    trie.insert("hypersonic", frequency=10)
    trie.insert("propulsion", frequency=15)
    trie.insert("consensus", frequency=8)

    matcher = TrieFuzzyMatcher(trie)

    # Typo: "hypersonik" (distance 1 to "hypersonic")
    suggestion = matcher.suggest_correction("hypersonik")
    assert suggestion == "hypersonic"

    # Already valid word returns None
    assert matcher.suggest_correction("propulsion") is None

    # Too distant word returns None
    assert matcher.suggest_correction("completelydifferentword", max_distance=2) is None
