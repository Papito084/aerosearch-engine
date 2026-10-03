"""High-performance text tokenizer and normalizer with position tracking."""

import re
import unicodedata

from aerosearch.core.models import Token
from aerosearch.core.text.stemmer import PorterStemmer
from aerosearch.core.text.stopwords import StopWordsFilter

# Pattern matching words including internal hyphens/dots (e.g. "covid-19", "v1.2", "in-memory")
WORD_PATTERN = re.compile(r"[a-zA-Z0-9]+(?:[-_'][a-zA-Z0-9]+)*")


class Tokenizer:
    """Robust tokenizer and text normalizer for full-text indexing and querying."""

    def __init__(
        self,
        stopwords_filter: StopWordsFilter | None = None,
        stemmer: PorterStemmer | None = None,
        enable_stemming: bool = True,
        enable_stopwords: bool = True,
        strip_accents: bool = True,
        min_token_len: int = 1,
        max_token_len: int = 50,
    ) -> None:
        self.stopwords_filter = stopwords_filter or StopWordsFilter(enabled=enable_stopwords)
        self.stemmer = stemmer or PorterStemmer()
        self.enable_stemming = enable_stemming
        self.enable_stopwords = enable_stopwords
        self.strip_accents = strip_accents
        self.min_token_len = min_token_len
        self.max_token_len = max_token_len

    def normalize_text(self, text: str) -> str:
        """Strip accents, lowercase, and clean text."""
        if not text:
            return ""
        if self.strip_accents:
            # Decompose unicode characters into base char + diacritic marks, then discard marks
            text = unicodedata.normalize("NFKD", text)
            text = "".join(c for c in text if not unicodedata.combining(c))
        return text.lower()

    def tokenize(self, text: str, field_name: str = "content") -> list[Token]:
        """Tokenize input text into a sequence of normalized and stemmed Token objects."""
        if not text:
            return []

        clean_text = self.normalize_text(text)
        tokens: list[Token] = []
        token_pos = 0

        for match in WORD_PATTERN.finditer(clean_text):
            raw_word = match.group(0)
            word_len = len(raw_word)

            if word_len < self.min_token_len or word_len > self.max_token_len:
                continue

            if self.enable_stopwords and self.stopwords_filter.is_stop_word(raw_word):
                token_pos += 1
                continue

            stemmed_word = self.stemmer.stem(raw_word) if self.enable_stemming else raw_word

            tokens.append(
                Token(
                    raw=raw_word,
                    normalized=raw_word,
                    stemmed=stemmed_word,
                    position=token_pos,
                    field_name=field_name,
                )
            )
            token_pos += 1

        return tokens

    def tokenize_query(self, query: str) -> list[Token]:
        """Tokenize a search query without advancing empty positions."""
        if not query:
            return []

        clean_query = self.normalize_text(query)
        tokens: list[Token] = []
        pos = 0

        for match in WORD_PATTERN.finditer(clean_query):
            word = match.group(0)
            if len(word) < self.min_token_len:
                continue

            # Allow query tokens even if stop word when query has only 1 word
            is_stop = self.stopwords_filter.is_stop_word(word)
            if self.enable_stopwords and is_stop:
                continue

            stemmed_word = self.stemmer.stem(word) if self.enable_stemming else word
            tokens.append(
                Token(
                    raw=word,
                    normalized=word,
                    stemmed=stemmed_word,
                    position=pos,
                    field_name="query",
                )
            )
            pos += 1

        # Fallback: if all query terms were filtered out as stop words (e.g. "the"), keep them unstemmed
        if not tokens and query.strip():
            for match in WORD_PATTERN.finditer(clean_query):
                word = match.group(0)
                tokens.append(
                    Token(
                        raw=word,
                        normalized=word,
                        stemmed=word,
                        position=len(tokens),
                        field_name="query",
                    )
                )

        return tokens
