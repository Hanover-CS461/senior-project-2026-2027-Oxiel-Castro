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
    COLOR_END_BG,
    DEFEAT_FRAME,
    DEFEAT_SCALE,
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

        self.enemy_frames = {
            key: load_frames(
                spec["path"],
                spec["frames"],
                scale=spec["scale"],
                flip=(key in ("fly", "snake")),
                normalize=True,
            )
            for key, spec in ENEMY_SPRITES.items()
        }
        self.luna_sheet = None
        self._luna_cache = {}
        self.set_luna_sheet(LUNA_SHEET)

    def _build_luna_frames(self, sheet_path):
        """Crop every Luna animation from a sheet, keyed by attribute name."""
        return {
            "luna_frames": load_frames(sheet_path, LUNA_FRAMES, size=(132, 96)),
            "walk_frames": load_frames(sheet_path, WALK_FRAMES, scale=5),
            "luna_attack_frames": load_frames(sheet_path, ATTACK_FRAMES, scale=5),
            "map_idle_frames": load_frames(sheet_path, LUNA_FRAMES, scale=2),
            "map_walk_frames": load_frames(sheet_path, WALK_FRAMES, scale=2),
            "defeat_frame": load_frames(sheet_path, [DEFEAT_FRAME], scale=DEFEAT_SCALE)[
                0
            ],
        }

    def set_luna_sheet(self, sheet_path):
        """Switch Luna's sprite sheet, caching frames and rebuilding defeat art."""
        if sheet_path == self.luna_sheet:
            return
        frames = self._luna_cache.get(sheet_path)
        if frames is None:
            frames = self._build_luna_frames(sheet_path)
            self._luna_cache[sheet_path] = frames
        for name, value in frames.items():
            setattr(self, name, value)
        self.luna_sheet = sheet_path
        self.defeat_background = pygame.Surface(WINDOW_SIZE)
        self.defeat_background.fill(COLOR_END_BG)
        self.defeat_background.blit(
            self.defeat_frame,
            self.defeat_frame.get_rect(center=(WINDOW_SIZE[0] // 2, 140)),
        )

    def scene_image(self, path):
        """Load and cache a scene image, falling back to the menu background."""
        try:
            return load_image(path, WINDOW_SIZE)
        except (pygame.error, FileNotFoundError, TypeError):
            return self.background
