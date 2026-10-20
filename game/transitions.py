"""Screen transitions: through-black fades, spirals, and radial wipes.

Each transition runs a callback at its black/reveal moment, which the
state machine uses to swap screens. Spiral and wipe share the same
swept-wedge geometry, built once in swept_points.
"""

import math

import pygame

from config import FADE_TIME, SPIRAL_TIME, WINDOW_SIZE, WIPE_TIME


def swept_points(center, radius, start_angle, swept):
    """Return polygon points for a wedge swept by degrees from start_angle."""
    cx, cy = center
    steps = max(1, int(swept / 6))
    points = [(cx, cy)]
    for i in range(steps + 1):
        angle = math.radians(start_angle + swept * i / steps)
        points.append(
            (int(cx + radius * math.cos(angle)), int(cy + radius * math.sin(angle)))
        )
    return points


class Transitions:
    """Owns the fade, spiral, and wipe transitions and their draw state."""

    def __init__(self):
        """Prepare the black overlay surfaces and clear all transitions."""
        self.fade_phase = None
        self.fade_start = 0
        self.fade_next = None
        self.fade_surface = pygame.Surface(WINDOW_SIZE)
        self.fade_surface.fill((0, 0, 0))
        self.black_surface = pygame.Surface(WINDOW_SIZE)
        self.black_surface.fill((0, 0, 0))
        self.spiral = None
        self.wipe = None
        self._center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)

    @property
    def fade_active(self):
        """Return True while a fade is running."""
        return self.fade_phase is not None

    @property
    def busy(self):
        """Return True while any transition is running, to block input."""
        return self.fade_phase is not None or self.wipe is not None or self.spiral is not None

    def start_fade(self, next_action):
        """Begin a through-black fade, running next_action at full black."""
        if self.fade_phase is not None:
            return
        self.fade_phase = "out"
        self.fade_start = pygame.time.get_ticks()
        self.fade_next = next_action

    def start_spiral(self, next_action):
        """Begin a black spiral fade, running next_action once fully black."""
        if self.spiral is not None:
            return
        self.spiral = {
            "start": pygame.time.get_ticks(),
            "center": self._center,
            "radius": 540,
            "start_angle": -90,
            "next": next_action,
        }

    def start_wipe(self, next_action, screen, from_surface=None):
        """Begin a rotating radial wipe, running next_action immediately."""
        self.wipe = {
            "from": from_surface if from_surface is not None else screen.copy(),
            "start": pygame.time.get_ticks(),
            "center": self._center,
            "radius": 540,
            "start_angle": -90,
        }
        next_action()

    def draw(self, screen):
        """Draw every active transition overlay, back to front."""
        self._draw_spiral(screen)
        self._draw_wipe(screen)
        self._draw_fade(screen)

    def _draw_fade(self, screen):
        """Overlay a black surface whose alpha animates the fade."""
        if self.fade_phase is None:
            return
        now = pygame.time.get_ticks()
        progress = min(1.0, (now - self.fade_start) / FADE_TIME)
        if self.fade_phase == "out":
            alpha = int(255 * progress)
            if progress >= 1.0:
                action, self.fade_next = self.fade_next, None
                if action:
                    action()
                self.fade_phase = "in"
                self.fade_start = now
        else:
            alpha = int(255 * (1.0 - progress))
            if progress >= 1.0:
                self.fade_phase = None
        if alpha > 0:
            self.fade_surface.set_alpha(alpha)
            screen.blit(self.fade_surface, (0, 0))

    def _draw_spiral(self, screen):
        """Swirl a growing black wedge over the screen, then run the callback."""
        if self.spiral is None:
            return
        now = pygame.time.get_ticks()
        progress = min(1.0, (now - self.spiral["start"]) / SPIRAL_TIME)
        mask = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        points = swept_points(
            self.spiral["center"],
            self.spiral["radius"],
            self.spiral["start_angle"],
            progress * 360.0,
        )
        if len(points) >= 3:
            pygame.draw.polygon(mask, (0, 0, 0, 255), points)
        screen.blit(mask, (0, 0))
        if progress >= 1.0:
            action, self.spiral = self.spiral["next"], None
            if action:
                action()

    def _draw_wipe(self, screen):
        """Reveal the current screen through a growing, rotating wedge."""
        if self.wipe is None:
            return
        now = pygame.time.get_ticks()
        progress = min(1.0, (now - self.wipe["start"]) / WIPE_TIME)
        mask = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        mask.fill((255, 255, 255, 255))
        points = swept_points(
            self.wipe["center"],
            self.wipe["radius"],
            self.wipe["start_angle"],
            progress * 360.0,
        )
        if len(points) >= 3:
            pygame.draw.polygon(mask, (255, 255, 255, 0), points)
        layer = self.wipe["from"].convert_alpha()
        layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(layer, (0, 0))
        if progress >= 1.0:
            self.wipe = None
