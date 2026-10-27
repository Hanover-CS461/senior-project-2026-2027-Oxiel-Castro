"""Hit and heal feedback: floating numbers, sparkle particles, screen shake,
and sprite silhouettes used for hit flashes and status auras.

These are presentation-only: they read positions and timestamps from the
battle view and never change combat state.
"""

import random

import pygame

from config import COLOR_BLACK
from ui import flash_surface

POPUP_TIME = 750
POPUP_RISE = 54
SHAKE_TIME = 220
SHAKE_MAG = 6
HEAL_SPARKLES = 12
SPARKLE_TIME = 650
DODGE_TIME = 300
DODGE_HOP = 26
SPARKLE_BASE_Y = 340
DEATH_DUST = 12


class Effects:
    """Owns short-lived visual feedback: popups, particles, shake, and flashes."""

    def __init__(self):
        """Start with no active effects and an empty silhouette cache."""
        self.popups = []
        self.particles = []
        self.shake_until = 0
        self._flash_cache = {}

    def reset(self):
        """Clear popups, particles, and shake for a fresh battle."""
        self.popups = []
        self.particles = []
        self.shake_until = 0

    def flash(self, frame, color):
        """Return a cached solid-color silhouette of a frame."""
        key = (id(frame), color)
        surf = self._flash_cache.get(key)
        if surf is None:
            surf = flash_surface(frame, color)
            self._flash_cache[key] = surf
        return surf

    def blit_flash(self, screen, frame, pos, color, alpha):
        """Blit a solid-color silhouette of a sprite over it as a tint/flash."""
        flash = self.flash(frame, color)
        flash.set_alpha(max(0, min(255, int(alpha))))
        screen.blit(flash, pos)

    def dodge_offset(self, now, until, direction):
        """Return (dx, dy) for a quick side-hop while dodging."""
        if now >= until:
            return 0, 0
        progress = (DODGE_TIME - (until - now)) / DODGE_TIME
        phase = 1 - abs(2 * progress - 1)
        return direction * int(DODGE_HOP * phase), -int(DODGE_HOP * 0.5 * phase)

    def shake(self, now):
        """Start a brief screen shake."""
        self.shake_until = now + SHAKE_TIME

    def spawn_popup(self, text, x, y, color):
        """Add a floating text popup above a combatant."""
        self.popups.append({
            "text": text,
            "x": x,
            "y": y,
            "start": pygame.time.get_ticks(),
            "color": color,
        })

    def spawn_heal(self, amount, luna_x):
        """Show a heal number and a burst of green sparkles over Luna."""
        self.spawn_gain(amount, (80, 230, 120), luna_x, 300)

    def spawn_focus(self, amount, luna_x):
        """Show a focus number and a burst of blue sparkles over Luna."""
        self.spawn_gain(amount, (90, 170, 255), luna_x, 266)

    def spawn_gain(self, amount, color, luna_x, popup_y):
        """Spawn a +N popup and a matching burst of sparkles over Luna."""
        now = pygame.time.get_ticks()
        self.spawn_popup(f"+{amount}", luna_x + 36, popup_y, color)
        for _ in range(HEAL_SPARKLES):
            self.particles.append({
                "x": luna_x + random.randint(0, 120),
                "y": SPARKLE_BASE_Y + random.randint(0, 80),
                "vx": random.uniform(-25, 25),
                "vy": random.uniform(-80, -30),
                "start": now,
                "color": color,
            })

    def spawn_death_dust(self, enemy_x, feet_y):
        """Puff of dust at the enemy's feet when it collapses."""
        now = pygame.time.get_ticks()
        for _ in range(DEATH_DUST):
            self.particles.append({
                "x": enemy_x + random.randint(-30, 30),
                "y": feet_y - random.randint(0, 10),
                "vx": random.uniform(-45, 45),
                "vy": random.uniform(-55, -15),
                "start": now,
                "color": (185, 170, 145),
            })

    def draw_popups(self, screen, font, now):
        """Draw and expire floating damage numbers."""
        alive = []
        for popup in self.popups:
            age = now - popup["start"]
            if age > POPUP_TIME:
                continue
            frac = age / POPUP_TIME
            y = popup["y"] - int(POPUP_RISE * frac)
            alpha = int(255 * (1 - frac))
            shadow = font.render(popup["text"], True, COLOR_BLACK)
            shadow.set_alpha(alpha)
            text = font.render(popup["text"], True, popup["color"])
            text.set_alpha(alpha)
            screen.blit(shadow, (popup["x"] + 2, y + 2))
            screen.blit(text, (popup["x"], y))
            alive.append(popup)
        self.popups = alive

    def draw_particles(self, screen, now):
        """Draw and expire the little sparkle particles (heals)."""
        alive = []
        for p in self.particles:
            age = now - p["start"]
            if age > SPARKLE_TIME:
                continue
            frac = age / SPARKLE_TIME
            x = p["x"] + p["vx"] * age / 1000.0
            y = p["y"] + p["vy"] * age / 1000.0
            alpha = int(255 * (1 - frac))
            size = 3
            spark = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(spark, (*p["color"], alpha), (size, size), size)
            screen.blit(spark, (int(x) - size, int(y) - size))
            alive.append(p)
        self.particles = alive

    def apply_shake(self, screen, now):
        """Jitter the whole frame briefly after a heavy hit."""
        if now >= self.shake_until:
            return
        mag = SHAKE_MAG if (self.shake_until - now) > SHAKE_TIME // 2 else SHAKE_MAG // 2
        snap = screen.copy()
        screen.fill(COLOR_BLACK)
        screen.blit(snap, (random.randint(-mag, mag), random.randint(-mag, mag)))
