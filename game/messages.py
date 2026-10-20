"""Battle narration paging.

Splits the ever-growing battle message into wrapped, timed pages so the
battle screen can reveal it a few lines at a time. Owns only the paging
state; the caller supplies the current message and the frame time.
"""

import re

from config import MESSAGE_MAX_WIDTH, MESSAGE_PAGE_LINES, READ_DELAY
from ui import wrap_lines


class MessageLog:
    """Pages a battle narration string into wrapped, timed pages."""

    def __init__(self, font):
        """Create an empty log that wraps text with the given font."""
        self.font = font
        self._pages = []
        self._page = 0
        self._timer = 0
        self._last = None

    def reset(self):
        """Clear all paging state for a fresh battle."""
        self._pages = []
        self._page = 0
        self._timer = 0
        self._last = None

    def sync(self, message, now):
        """Rebuild the pages whenever the battle message changes."""
        if message == self._last:
            return
        self._last = message
        sentences = [s for s in re.split(r"(?<=[.!])\s+", message) if s]
        lines = wrap_lines(sentences, self.font, MESSAGE_MAX_WIDTH)
        self._pages = [
            lines[i : i + MESSAGE_PAGE_LINES]
            for i in range(0, len(lines), MESSAGE_PAGE_LINES)
        ]
        self._page = 0
        self._timer = now

    def advance(self, now):
        """Advance to the next page of the log after a pause."""
        if self._page < len(self._pages) - 1 and now - self._timer > READ_DELAY:
            self._page += 1
            self._timer = now

    def done(self):
        """Return True once the final page is being shown."""
        return not self._pages or self._page >= len(self._pages) - 1

    def read_out(self, now):
        """Return True once the final page has been shown for READ_DELAY."""
        return self.done() and now - self._timer > READ_DELAY

    def lines(self, fallback):
        """Return the lines of the current page, or [fallback] if empty."""
        return self._pages[self._page] if self._pages else [fallback]

    @property
    def has_more(self):
        """Return True when pages remain after the current one."""
        return len(self._pages) > self._page + 1
