"""Prologue story: scene data and pure progression for the intro cutscene.

This module is pygame-free. main.py owns the timers, the through-black
fades, and input; here we only hold the scenes and answer, for a given
elapsed time, which line of the current scene is showing.

Lines replace one another: each stays on screen for SCENE_LINE_TIME ms
before the next takes its place. A scene is revealed once its final line
has been reached.
"""

SCENE_LINE_TIME = 3000

SCENES = [
    {
        "image": "game/assets/images/scene_1.1.png",
        "lines": [
            "Luna slept curled on her cat tree, warm in the afternoon light.",
            "Her human, Oxiel, had gone out on one of his usual adventures.",
            "He always came back before dark.",
        ],
    },
    {
        "image": "game/assets/images/scene_2.png",
        "lines": [
            "When Luna woke, the light was gone and the house was quiet.",
            "No footsteps. No jingling keys. No dinner.",
            "Oxiel had never stayed away this long.",
        ],
    },
    {
        "image": "game/assets/images/Sigma Chi House and Wandering Cat.png",
        "lines": [
            "Luna had never left the comfort of her building. The campus was a mystery.",
            "But Oxiel might be in danger, or simply late. Either way, she had to know.",
            "So the little indoor cat slipped out the door and went looking.",
        ],
    },
]


class Story:
    """Tracks which intro scene is showing and whether the intro is done."""

    def __init__(self, scenes=None):
        """Start at the first scene with nothing finished."""
        self.scenes = list(scenes) if scenes is not None else list(SCENES)
        self.index = 0
        self.finished = False

    def scene(self):
        """Return the current scene dict, or None once the intro is over."""
        if self.finished or self.index >= len(self.scenes):
            return None
        return self.scenes[self.index]

    def lines(self):
        """Return the current scene's lines, empty once finished."""
        scene = self.scene()
        return scene["lines"] if scene else []

    def line_count(self):
        """Return how many lines the current scene has."""
        return len(self.lines())

    def line_index(self, elapsed):
        """Return the index of the line visible after elapsed milliseconds."""
        count = self.line_count()
        if count == 0:
            return 0
        return min(elapsed // SCENE_LINE_TIME, count - 1)

    def visible_line(self, elapsed):
        """Return the single line visible after elapsed milliseconds."""
        lines = self.lines()
        if not lines:
            return None
        return lines[self.line_index(elapsed)]

    def reveal_done(self, elapsed):
        """Return True once the scene's final line has been reached."""
        count = self.line_count()
        return count <= 1 or elapsed >= (count - 1) * SCENE_LINE_TIME

    def snap(self):
        """Return the elapsed time at which the final line is showing."""
        count = self.line_count()
        if count <= 1:
            return 0
        return (count - 1) * SCENE_LINE_TIME

    def advance(self):
        """Move to the next scene, returning False once the intro is over."""
        if self.finished:
            return False
        self.index += 1
        if self.index >= len(self.scenes):
            self.finished = True
            return False
        return True

    def skip(self):
        """End the intro immediately."""
        self.finished = True
        self.index = len(self.scenes)
