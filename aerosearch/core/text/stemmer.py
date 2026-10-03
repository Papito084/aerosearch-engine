"""Pure-Python implementation of the Porter Stemmer algorithm (Porter 1980).

Ref: Porter, M. "An algorithm for suffix stripping." Program 14.3 (1980): 130-137.
Zero external dependencies, highly optimized with LRU caching.
"""

from functools import lru_cache


class PorterStemmer:
    """Algorithmic lightweight English Porter Stemmer with caching."""

    VOWELS = frozenset("aeiou")

    @classmethod
    def _is_consonant(cls, word: str, i: int) -> bool:
        """Return True if word[i] is a consonant."""
        ch = word[i]
        if ch in cls.VOWELS:
            return False
        if ch == "y":
            if i == 0:
                return True
            return not cls._is_consonant(word, i - 1)
        return True

    @classmethod
    def _measure(cls, stem: str) -> int:
        """Calculate the measure m of a stem [c](vc)^m[v]."""
        if not stem:
            return 0
        pattern = []
        for i in range(len(stem)):
            pattern.append("c" if cls._is_consonant(stem, i) else "v")

        # Collapse consecutive identical types
        condensed: list[str] = []
        for c in pattern:
            if not condensed or condensed[-1] != c:
                condensed.append(c)


        # Count occurrences of 'vc'
        s = "".join(condensed)
        return s.count("vc")

    @classmethod
    def _contains_vowel(cls, stem: str) -> bool:
        """Return True if stem contains at least one vowel."""
        for i in range(len(stem)):
            if not cls._is_consonant(stem, i):
                return True
        return False

    @classmethod
    def _ends_double_consonant(cls, stem: str) -> bool:
        """Return True if stem ends with a double consonant (*d)."""
        if len(stem) < 2:
            return False
        if stem[-1] != stem[-2]:
            return False
        return cls._is_consonant(stem, len(stem) - 1)

    @classmethod
    def _ends_cvc(cls, stem: str) -> bool:
        """Return True if stem ends with consonant-vowel-consonant where second c is not w, x, y."""
        if len(stem) < 3:
            return False
        c1 = cls._is_consonant(stem, len(stem) - 3)
        v = not cls._is_consonant(stem, len(stem) - 2)
        c2 = cls._is_consonant(stem, len(stem) - 1)
        if c1 and v and c2:
            if stem[-1] not in ("w", "x", "y"):
                return True
        return False

    @classmethod
    def _step1a(cls, word: str) -> str:
        if word.endswith("sses"):
            return word[:-2]
        if word.endswith("ies"):
            return word[:-2]
        if word.endswith("ss"):
            return word
        if word.endswith("s"):
            return word[:-1]
        return word

    @classmethod
    def _step1b(cls, word: str) -> str:
        if word.endswith("eed"):
            stem = word[:-3]
            if cls._measure(stem) > 0:
                return stem + "ee"
            return word

        second_or_third = False
        stem = ""
        if word.endswith("ed"):
            stem = word[:-2]
            if cls._contains_vowel(stem):
                word = stem
                second_or_third = True
        elif word.endswith("ing"):
            stem = word[:-3]
            if cls._contains_vowel(stem):
                word = stem
                second_or_third = True

        if second_or_third:
            if word.endswith("at") or word.endswith("bl") or word.endswith("iz"):
                return word + "e"
            if cls._ends_double_consonant(word) and not (
                word.endswith("l") or word.endswith("s") or word.endswith("z")
            ):
                return word[:-1]
            if cls._measure(word) == 1 and cls._ends_cvc(word):
                return word + "e"
        return word

    @classmethod
    def _step1c(cls, word: str) -> str:
        if word.endswith("y"):
            stem = word[:-1]
            if cls._contains_vowel(stem):
                return stem + "i"
        return word

    @classmethod
    def _step2(cls, word: str) -> str:
        pairs = [
            ("ational", "ate"),
            ("tional", "tion"),
            ("enci", "ence"),
            ("anci", "ance"),
            ("izer", "ize"),
            ("abli", "able"),
            ("alli", "al"),
            ("entli", "ent"),
            ("eli", "e"),
            ("ousli", "ous"),
            ("ization", "ize"),
            ("ation", "ate"),
            ("ator", "ate"),
            ("alism", "al"),
            ("iveness", "ive"),
            ("fulness", "ful"),
            ("ousness", "ous"),
            ("aliti", "al"),
            ("iviti", "ive"),
            ("biliti", "ble"),
        ]
        for suffix, replacement in pairs:
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                if cls._measure(stem) > 0:
                    return stem + replacement
                return word
        return word

    @classmethod
    def _step3(cls, word: str) -> str:
        pairs = [
            ("icate", "ic"),
            ("ative", ""),
            ("alize", "al"),
            ("iciti", "ic"),
            ("ical", "ic"),
            ("ful", ""),
            ("ness", ""),
        ]
        for suffix, replacement in pairs:
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                if cls._measure(stem) > 0:
                    return stem + replacement
                return word
        return word

    @classmethod
    def _step4(cls, word: str) -> str:
        suffixes = [
            "al",
            "ance",
            "ence",
            "er",
            "ic",
            "able",
            "ible",
            "ant",
            "ement",
            "ment",
            "ent",
            "ou",
            "ism",
            "ate",
            "iti",
            "ous",
            "ive",
            "ize",
        ]
        for suffix in suffixes:
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                if cls._measure(stem) > 1:
                    return stem
                return word

        if word.endswith("ion"):
            stem = word[:-3]
            if cls._measure(stem) > 1 and (stem.endswith("s") or stem.endswith("t")):
                return stem

        return word

    @classmethod
    def _step5a(cls, word: str) -> str:
        if word.endswith("e"):
            stem = word[:-1]
            m = cls._measure(stem)
            if m > 1:
                return stem
            if m == 1 and not cls._ends_cvc(stem):
                return stem
        return word

    @classmethod
    def _step5b(cls, word: str) -> str:
        if cls._measure(word) > 1 and cls._ends_double_consonant(word) and word.endswith("l"):
            return word[:-1]
        return word

    @classmethod
    @lru_cache(maxsize=32768)
    def stem(cls, word: str) -> str:
        """Stem a word using Porter algorithm. Caches repeated lookups."""
        if len(word) <= 2:
            return word

        w = word.lower()
        w = cls._step1a(w)
        w = cls._step1b(w)
        w = cls._step1c(w)
        w = cls._step2(w)
        w = cls._step3(w)
        w = cls._step4(w)
        w = cls._step5a(w)
        w = cls._step5b(w)
        return w
