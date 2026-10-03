"""Unit tests for HitHighlighter snippet generation and tag wrapping."""

from aerosearch.core.scoring.highlighter import HitHighlighter


def test_highlighter_basic_match() -> None:
    highlighter = HitHighlighter(snippet_length=100)
    text = "Raft is a distributed consensus algorithm."
    snippet = highlighter.generate_snippet(text, ["consensus"])
    assert "<mark" in snippet
    assert "consensus" in snippet
    assert "</mark>" in snippet


def test_highlighter_html_safety() -> None:
    highlighter = HitHighlighter()
    malicious = "<script>alert('xss')</script> and database search."
    snippet = highlighter.generate_snippet(malicious, ["search"])
    assert "<script>" not in snippet
    assert "&lt;script&gt;" in snippet
    assert "<mark" in snippet


def test_highlighter_long_text_density_window() -> None:
    highlighter = HitHighlighter(snippet_length=80)
    # Long text where target is deep in the content
    intro = "Introductory text without matches " * 10
    target = "Here is the critical supersonic propulsion breakthrough in aeronautics. "
    outro = "Conclusion text without matches " * 10
    full_text = f"{intro}{target}{outro}"

    snippet = highlighter.generate_snippet(full_text, ["supersonic", "propulsion"])
    assert "supersonic" in snippet
    assert "propulsion" in snippet
    assert "<mark" in snippet
