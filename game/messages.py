"""Battle narration display.

Keeps only the most recent lines of the ever-growing battle message and
reveals new lines on a fixed cadence, so every line stays on screen for
the same amount of time instead of flashing by at animation speed.
"""

import re

from config import (
    MESSAGE_HOLD,
    MESSAGE_MAX_LINES,
    MESSAGE_MAX_WIDTH,
    READ_DELAY,
)
from ui import wrap_lines


class MessageLog:
    """Reveals the most recent lines of a battle narration on a fixed cadence."""

    def __init__(self, font, max_lines=MESSAGE_MAX_LINES):
        """Create an empty log that wraps text with the given font."""
        self.font = font
        self.max_lines = max_lines
        self._lines = []
        self._queue = []
        self._timer = 0
        self._last = None

    def reset(self):
        """Clear all state for a fresh battle."""
        self._lines = []
        self._queue = []
        self._timer = 0
        self._last = None

    def sync(self, message, now):
        """Queue the latest lines whenever the battle message changes."""
        if message == self._last:
            return
        self._last = message
        sentences = [s for s in re.split(r"(?<=[.!])\s+", message) if s]
        lines = wrap_lines(sentences, self.font, MESSAGE_MAX_WIDTH)[-self.max_lines:]
        if lines and lines != self._lines and lines != self._queue[-1:]:
            self._queue.append(lines)

    def advance(self, now):
        """Reveal the next queued lines once the current ones have been held."""
        if not self._queue:
            return
        if not self._lines or now - self._timer >= MESSAGE_HOLD:
            self._lines = self._queue.pop(0)
            self._timer = now

    def done(self):
        """Return True once no queued lines remain."""
        return not self._queue

    def read_out(self, now):
        """Return True once the final lines have been held for READ_DELAY."""
        return self.done() and now - self._timer > READ_DELAY

    def lines(self, fallback=None):
        """Return the lines currently on screen."""
        return self._lines

    @property
    def has_more(self):
        """Return True while lines are still queued."""
        return bool(self._queue)
