"""Prefix Tree (Trie) for high-speed prefix search and autocomplete."""

import heapq
from dataclasses import dataclass, field


@dataclass
class TrieNode:
    """Node in the Prefix Tree."""

    children: dict[str, "TrieNode"] = field(default_factory=dict)
    is_end: bool = False
    frequency: int = 0
    word: str | None = None


class Trie:
    """High-performance Prefix Tree (Trie) supporting frequency-ranked autocomplete."""

    def __init__(self) -> None:
        self.root = TrieNode()
        self._total_words: int = 0

    def insert(self, word: str, frequency: int = 1) -> None:
        """Insert a word with an associated frequency weight."""
        if not word:
            return

        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]

        if not current.is_end:
            current.is_end = True
            current.word = word
            current.frequency = frequency
            self._total_words += 1
        else:
            current.frequency += frequency

    def search(self, word: str) -> bool:
        """Check if exact word exists in Trie."""
        node = self._find_node(word)
        return node is not None and node.is_end

    def get_frequency(self, word: str) -> int:
        """Get term frequency stored for exact word."""
        node = self._find_node(word)
        if node and node.is_end:
            return node.frequency
        return 0

    def _find_node(self, prefix: str) -> TrieNode | None:
        """Traverse to the node representing the prefix, if it exists."""
        current = self.root
        for char in prefix:
            if char not in current.children:
                return None
            current = current.children[char]
        return current

    def autocomplete(self, prefix: str, limit: int = 10) -> list[tuple[str, int]]:
        """Return top `limit` completions for `prefix`, sorted by descending frequency."""
        if not prefix:
            node = self.root
        else:
            found_node = self._find_node(prefix.lower())
            if not found_node:
                return []
            node = found_node


        # Min-heap to maintain top K items: (frequency, word)
        heap: list[tuple[int, str]] = []

        stack = [node]
        while stack:
            curr = stack.pop()
            if curr.is_end and curr.word:
                if len(heap) < limit:
                    heapq.heappush(heap, (curr.frequency, curr.word))
                elif curr.frequency > heap[0][0]:
                    heapq.heapreplace(heap, (curr.frequency, curr.word))

            for child in curr.children.values():
                stack.append(child)

        # Sort descending by frequency
        sorted_results = sorted(heap, key=lambda x: (-x[0], x[1]))
        return [(word, freq) for freq, word in sorted_results]

    def get_all_words(self) -> list[str]:
        """Return all complete words stored in the Trie."""
        words: list[str] = []
        stack = [self.root]
        while stack:
            curr = stack.pop()
            if curr.is_end and curr.word:
                words.append(curr.word)
            stack.extend(curr.children.values())
        return words

    def __len__(self) -> int:
        """Total unique words stored in the Trie."""
        return self._total_words
