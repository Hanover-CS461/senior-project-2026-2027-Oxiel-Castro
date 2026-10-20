"""Asset loading.

Loads and holds every image and sprite frame the game draws, so main.py
can focus on state and input. Scaled frames are built once at startup.
"""

import pygame

from config import (
    ATTACK_FRAMES,
    BACKGROUND_IMAGE,
    BATTLE_BACKGROUNDS,
    BATTLE_BG,
    CAMPUS_IMAGE,
    ENEMY_SPRITES,
    LUNA_FRAMES,
    LUNA_SHEET,
    WALK_FRAMES,
    WINDOW_SIZE,
)
from sprites import load_frames, load_image


class Assets:
    """Loads and holds every image and sprite frame the game draws."""

    def __init__(self):
        """Load the backgrounds and sprite sheets used across all screens."""
        self.background = load_image(BACKGROUND_IMAGE, WINDOW_SIZE)
        self.battle_bg = load_image(BATTLE_BG, WINDOW_SIZE)
        self.battle_backgrounds = {
            path: load_image(path, WINDOW_SIZE)
            for spec in BATTLE_BACKGROUNDS.values()
            for path in spec.values()
        }
        self.campus_bg = load_image(CAMPUS_IMAGE, WINDOW_SIZE)

        self.luna_frames = load_frames(LUNA_SHEET, LUNA_FRAMES, size=(132, 96))
        self.walk_frames = load_frames(LUNA_SHEET, WALK_FRAMES, scale=5)
        self.enemy_frames = {
            key: load_frames(
                spec["path"], spec["frames"], scale=spec["scale"],
                flip=(key in ("fly", "snake")), normalize=True,
            )
            for key, spec in ENEMY_SPRITES.items()
        }
        self.luna_attack_frames = load_frames(LUNA_SHEET, ATTACK_FRAMES, scale=5)
        self.map_idle_frames = load_frames(LUNA_SHEET, LUNA_FRAMES, scale=2)
        self.map_walk_frames = load_frames(LUNA_SHEET, WALK_FRAMES, scale=2)

    def scene_image(self, path):
        """Load and cache a scene image, falling back to the menu background."""
        try:
            return load_image(path, WINDOW_SIZE)
        except (pygame.error, FileNotFoundError, TypeError):
            return self.background
