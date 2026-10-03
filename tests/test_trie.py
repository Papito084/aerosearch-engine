"""Unit tests for Prefix Tree (Trie)."""

from aerosearch.core.structures.trie import Trie


def test_trie_insert_and_search() -> None:
    trie = Trie()
    trie.insert("aerospace")
    trie.insert("aerodynamic")
    trie.insert("algorithm")

    assert trie.search("aerospace") is True
    assert trie.search("aerodynamic") is True
    assert trie.search("aero") is False
    assert trie.search("unknown") is False
    assert len(trie) == 3


def test_trie_autocomplete_frequency_ranking() -> None:
    trie = Trie()
    trie.insert("search", frequency=5)
    trie.insert("searching", frequency=20)
    trie.insert("sea", frequency=2)
    trie.insert("season", frequency=1)

    results = trie.autocomplete("sea")
    words = [w for w, _ in results]

    # "searching" has highest freq (20), then "search" (5), then "sea" (2), then "season" (1)
    assert words == ["searching", "search", "sea", "season"]


def test_trie_empty_and_miss() -> None:
    trie = Trie()
    trie.insert("paxos")
    assert trie.autocomplete("raft") == []
