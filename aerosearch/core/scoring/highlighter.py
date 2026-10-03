"""Hit highlighting engine for extracting and highlighting matched snippets."""

import html
import re

HIGHLIGHT_OPEN = '<mark class="bg-amber-200 dark:bg-amber-800/80 text-amber-950 dark:text-amber-100 font-semibold px-1 py-0.5 rounded">'
HIGHLIGHT_CLOSE = "</mark>"


class HitHighlighter:
    """Extracts contextual snippets from text and highlights query matches."""

    def __init__(
        self,
        snippet_length: int = 180,
        tag_open: str = HIGHLIGHT_OPEN,
        tag_close: str = HIGHLIGHT_CLOSE,
    ) -> None:
        self.snippet_length = snippet_length
        self.tag_open = tag_open
        self.tag_close = tag_close

    def highlight_terms(self, text: str, query_terms: list[str]) -> str:
        """Surround all occurrences of query terms in text with highlighting tags."""
        if not text or not query_terms:
            return html.escape(text)

        # Filter out empty or very short terms
        terms = [re.escape(t.strip()) for t in query_terms if len(t.strip()) > 0]
        if not terms:
            return html.escape(text)

        # Build regex matching any query term on word boundaries or stems
        pattern = re.compile(rf"\b({'|'.join(terms)})\w*", re.IGNORECASE)

        # First escape HTML to prevent XSS
        safe_text = html.escape(text)

        # Substitute matches safely
        def replace_fn(match: re.Match[str]) -> str:
            return f"{self.tag_open}{match.group(0)}{self.tag_close}"

        return pattern.sub(replace_fn, safe_text)

    def generate_snippet(self, text: str, query_terms: list[str]) -> str:
        """Extract a high-relevance window containing matched terms with highlighting."""
        if not text:
            return ""

        clean_text = text.strip()
        if len(clean_text) <= self.snippet_length:
            return self.highlight_terms(clean_text, query_terms)

        valid_terms = [t.lower().strip() for t in query_terms if len(t.strip()) > 0]
        if not valid_terms:
            # If no terms, return start of text
            snippet = clean_text[: self.snippet_length].rsplit(" ", 1)[0]
            return html.escape(snippet) + "..."

        # Find all match positions in the text
        pattern = re.compile(
            rf"\b({'|'.join(re.escape(t) for t in valid_terms)})\w*", re.IGNORECASE
        )
        matches = list(pattern.finditer(clean_text))

        if not matches:
            # No match found in content (maybe match was in title or tags), return start
            snippet = clean_text[: self.snippet_length].rsplit(" ", 1)[0]
            return html.escape(snippet) + "..."

        # Best window search: evaluate windows of size `snippet_length` around each match
        best_start = 0
        best_score = -1

        for match in matches:
            # Center the window around this match
            start = max(0, match.start() - self.snippet_length // 3)
            end = min(len(clean_text), start + self.snippet_length)

            # Count matches in this window
            count = sum(1 for m in matches if start <= m.start() < end)
            if count > best_score:
                best_score = count
                best_start = start

        best_end = min(len(clean_text), best_start + self.snippet_length)

        # Adjust window boundaries to word boundaries
        if best_start > 0:
            space_pos = clean_text.find(" ", best_start)
            if space_pos != -1 and space_pos < best_start + 20:
                best_start = space_pos + 1

        if best_end < len(clean_text):
            rspace_pos = clean_text.rfind(" ", best_start, best_end)
            if rspace_pos != -1 and rspace_pos > best_end - 20:
                best_end = rspace_pos

        snippet_chunk = clean_text[best_start:best_end]

        prefix = "..." if best_start > 0 else ""
        suffix = "..." if best_end < len(clean_text) else ""

        highlighted_chunk = self.highlight_terms(snippet_chunk, query_terms)
        return f"{prefix}{highlighted_chunk}{suffix}"
