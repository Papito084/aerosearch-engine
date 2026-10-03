"""Fuzzy string matching and typo correction using Levenshtein & Trie-guided branch-and-bound."""

from aerosearch.core.structures.trie import Trie, TrieNode


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute classic Levenshtein distance between two strings with O(min(N, M)) memory."""
    if s1 == s2:
        return 0
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1] + [0] * len(s2)
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row[j + 1] = min(insertions, deletions, substitutions)
        previous_row = current_row

    return previous_row[-1]


def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Damerau-Levenshtein distance supporting insertions, deletions, substitutions, and transpositions."""
    len1, len2 = len(s1), len(s2)
    # 2D matrix
    d = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    for i in range(len1 + 1):
        d[i][0] = i
    for j in range(len2 + 1):
        d[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,  # deletion
                d[i][j - 1] + 1,  # insertion
                d[i - 1][j - 1] + cost,  # substitution
            )
            # Transposition check
            if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)

    return d[len1][len2]


class TrieFuzzyMatcher:
    """Trie-guided Levenshtein search for sub-millisecond 'Did you mean?' suggestions."""

    def __init__(self, trie: Trie) -> None:
        self.trie = trie

    def search_similar(
        self, target: str, max_distance: int = 2, max_results: int = 5
    ) -> list[tuple[str, int, int]]:
        """Search the Trie for words within max_distance of target.

        Returns list of tuples: (matched_word, edit_distance, frequency)
        sorted by: (edit_distance ASC, frequency DESC).
        """
        target = target.lower()
        results: list[tuple[str, int, int]] = []

        # Initial Levenshtein row: [0, 1, 2, ..., len(target)]
        initial_row = list(range(len(target) + 1))

        for char, child_node in self.trie.root.children.items():
            self._search_recursive(
                node=child_node,
                letter=char,
                target=target,
                previous_row=initial_row,
                results=results,
                max_distance=max_distance,
            )

        # Sort: first by smallest edit distance, then by highest corpus frequency
        results.sort(key=lambda item: (item[1], -item[2]))
        return results[:max_results]

    def _search_recursive(
        self,
        node: TrieNode,
        letter: str,
        target: str,
        previous_row: list[int],
        results: list[tuple[str, int, int]],
        max_distance: int,
    ) -> None:
        columns = len(target) + 1
        current_row = [previous_row[0] + 1] * columns

        # Build this row for the current letter in Trie
        for col in range(1, columns):
            insert_or_del = min(current_row[col - 1] + 1, previous_row[col] + 1)
            replace_cost = 0 if target[col - 1] == letter else 1
            replace = previous_row[col - 1] + replace_cost
            current_row[col] = min(insert_or_del, replace)

        # If current node is end of word and final distance <= max_distance, record it
        if current_row[-1] <= max_distance and node.is_end and node.word:
            results.append((node.word, current_row[-1], node.frequency))

        # Branch-and-bound: prune subtree if every element in current_row exceeds max_distance
        if min(current_row) <= max_distance:
            for next_char, next_node in node.children.items():
                self._search_recursive(
                    node=next_node,
                    letter=next_char,
                    target=target,
                    previous_row=current_row,
                    results=results,
                    max_distance=max_distance,
                )

    def suggest_correction(self, word: str, max_distance: int = 2) -> str | None:
        """Suggest single best correction for a word if not present in vocabulary."""
        if self.trie.search(word):
            return None  # Word already valid

        matches = self.search_similar(word, max_distance=max_distance, max_results=1)
        if matches:
            return matches[0][0]
        return None
