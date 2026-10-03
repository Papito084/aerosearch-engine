"""Unit tests for Tokenizer, Normalizer, and StopWordsFilter."""

from aerosearch.core.text.stopwords import StopWordsFilter
from aerosearch.core.text.tokenizer import Tokenizer


def test_stopwords_filter() -> None:
    filt = StopWordsFilter(languages=["en", "es"])
    assert filt.is_stop_word("the") is True
    assert filt.is_stop_word("el") is True
    assert filt.is_stop_word("aerodynamics") is False

    # Test custom words
    filt.add_words({"algorithm", "engine"})
    assert filt.is_stop_word("algorithm") is True
    filt.remove_words({"algorithm"})
    assert filt.is_stop_word("algorithm") is False


def test_tokenizer_normalization_and_accents() -> None:
    tok = Tokenizer(enable_stemming=False, enable_stopwords=False)
    # Spanish accents and punctuation
    text = "¡Hola! ¿Cómo estás? Programación rápida en Python."
    tokens = tok.tokenize(text)
    words = [t.normalized for t in tokens]
    assert "hola" in words
    assert "como" in words
    assert "estas" in words
    assert "programacion" in words
    assert "rapida" in words
    assert "python" in words


def test_tokenizer_position_tracking() -> None:
    tok = Tokenizer(enable_stemming=False, enable_stopwords=False)
    text = "zero one two three"
    tokens = tok.tokenize(text)
    assert len(tokens) == 4
    for i, t in enumerate(tokens):
        assert t.position == i


def test_tokenizer_query_fallback() -> None:
    tok = Tokenizer(enable_stemming=True, enable_stopwords=True)
    # If a query only has stop words (e.g. "the"), it should still produce a search token
    tokens = tok.tokenize_query("the")
    assert len(tokens) == 1
    assert tokens[0].raw == "the"
