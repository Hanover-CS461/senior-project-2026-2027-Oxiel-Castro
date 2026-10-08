"""Automated tests for the pure intro logic in game/story.py.

Run with:  python3 -m unittest discover -s tests
"""

import sys
from pathlib import Path
from unittest import TestCase

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "game"))

from story import SCENE_LINE_TIME, SCENES, Story


class StoryTest(TestCase):
    """Tests for scene progression and line reveal timing."""

    def test_starts_on_first_scene(self):
        story = Story()
        self.assertEqual(story.index, 0)
        self.assertFalse(story.finished)
        self.assertEqual(story.lines(), SCENES[0]["lines"])

    def test_first_line_visible_immediately(self):
        story = Story()
        self.assertEqual(story.visible_line(0), SCENES[0]["lines"][0])

    def test_lines_replace_over_time(self):
        story = Story()
        self.assertEqual(
            story.visible_line(SCENE_LINE_TIME), SCENES[0]["lines"][1]
        )
        self.assertEqual(
            story.visible_line(SCENE_LINE_TIME * 2), SCENES[0]["lines"][2]
        )

    def test_last_line_sticks(self):
        story = Story()
        self.assertEqual(
            story.visible_line(SCENE_LINE_TIME * 99), SCENES[0]["lines"][-1]
        )

    def test_reveal_not_done_until_last_line(self):
        story = Story()
        self.assertFalse(story.reveal_done(0))
        self.assertFalse(story.reveal_done(SCENE_LINE_TIME - 1))
        self.assertTrue(story.reveal_done(SCENE_LINE_TIME * 2))

    def test_snap_shows_final_line(self):
        story = Story()
        self.assertTrue(story.reveal_done(story.snap()))
        self.assertEqual(
            story.visible_line(story.snap()), SCENES[0]["lines"][-1]
        )

    def test_advance_walks_scenes_then_finishes(self):
        story = Story()
        self.assertTrue(story.advance())
        self.assertEqual(story.index, 1)
        self.assertTrue(story.advance())
        self.assertEqual(story.index, 2)
        self.assertFalse(story.advance())
        self.assertTrue(story.finished)
        self.assertIsNone(story.scene())

    def test_skip_ends_intro(self):
        story = Story()
        story.skip()
        self.assertTrue(story.finished)
        self.assertIsNone(story.visible_line(0))


if __name__ == "__main__":
    import unittest

    unittest.main()
