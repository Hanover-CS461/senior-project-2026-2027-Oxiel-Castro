"""Battle presentation: sprites, bars, menus, narration, and effects.

Owns everything that turns a Battle into what the player sees and clicks.
The run state decides when a fight starts and what its result means; this
view only reads and advances the Battle it is given.
"""

import pygame

from battle import Battle, ITEMS
from config import (
    COLOR_FOCUS_BAR,
    COLOR_HEAVY,
    COLOR_HINT,
    COLOR_HP_BAR,
    COLOR_WHITE,
    ENEMY_ATTACK_X,
    ENEMY_DELAY,
    ENEMY_X,
    LUNA_ATTACK_X,
    LUNA_X,
    MESSAGE_MAX_WIDTH,
    WALK_TIME,
)
from effects import DODGE_TIME, Effects
from messages import MessageLog
from ui import Button, draw_bar, draw_disabled_button, draw_outlined_text, wrap_lines

# Hit-feedback timing and sizing. Effect-specific tuning lives in effects.py.
HURT_TIME = 260
RECOIL = 16
TWEEN_RATE = 0.22
DEATH_TIME = 1000

# Status aura colors, in display priority order.
STATUS_AURA = (
    ("poisoned", (60, 220, 60)),
    ("webbed", (120, 170, 255)),
    ("riled", (255, 120, 30)),
    ("puffed", (255, 255, 255)),
    ("prowl", (0, 200, 255)),
    ("intimidated", (220, 40, 40)),
)

# Battle narration / tooltip layout.
MESSAGE_PANEL_X = 24
MESSAGE_PANEL_Y = 136
MESSAGE_PANEL_WIDTH = 752
MESSAGE_LINE_SPACING = 40
TOOLTIP_BOTTOM = 424


class BattleView:
    """Draws a battle, handles its menus, and animates the current turn."""

    def __init__(self, screen, assets, font, small_font):
        """Create the view and its menu buttons; start() supplies the battle."""
        self.screen = screen
        self.assets = assets
        self.font = font
        self.small_font = small_font
        self.battle = None
        self.background = None
        self.messages = MessageLog(self.small_font)
        self.effects = Effects()

        self.anim_index = 0
        self.anim_timer = 0
        self.enemy_anim_index = 0
        self.enemy_anim_timer = 0
        self.attack_state = None
        self.attack_index = 0
        self.attack_timer = 0
        self.walk_index = 0
        self.walk_timer = 0
        self.luna_x = LUNA_X
        self.enemy_x = ENEMY_X
        self.enemy_attack_state = None
        self.enemy_attack_timer = 0

        # Turn sequencing: an ordered list of steps resolved over animation
        # time, so damage lands on the contact frame rather than on click.
        self.turn_steps = []
        self.step_index = 0
        self.step_started = False
        self.step_resolved = False
        self.step_time = 0
        self.round_finished = False
        self.turn_active = False

        # Hit feedback: hurt flashes, floating numbers, bar tween, screen shake.
        self.enemy_hurt_until = 0
        self.luna_hurt_until = 0
        self.enemy_dodge_until = 0
        self.luna_dodge_until = 0
        self.enemy_hp_display = 0.0
        self.luna_hp_display = 0.0
        self.focus_display = 0.0
        self.death_start = None

        self.battle_buttons = [
            Button(20, 500, 150, 60, "Attack", "attack"),
            Button(175, 500, 150, 60, "Defend", "defend"),
            Button(330, 500, 150, 60, "Rest", "rest"),
            Button(485, 500, 150, 60, "Items", "items"),
            Button(640, 500, 150, 60, "Instincts", "instincts")
        ]
        self.instinct_spots = [
            ("night_vision", 140, 430),
            ("lick_wounds", 380, 430),
            ("yowl", 140, 490),
            ("nine_lives", 380, 490),
        ]
        self.instinct_buttons = [
            Button(x, y, 220, 55, f"{Battle.INSTINCTS[name]['name']} ({Battle.INSTINCTS[name]['cost']})", name)
            for name, x, y in self.instinct_spots
        ]
        self.item_buttons = [
            Button(x, y, 220, 55, f"{ITEMS[name]['name']} x0", name)
            for name, x, y in [("wet_food", 140, 430), ("catnip", 380, 430), ("milk", 140, 490)]
        ]
        self.back_button = Button(620, 430, 140, 55, "Back", "back")
        self.submenu = None

    def start(self, battle, background):
        """Bind a battle and background, then clear all presentation state."""
        self.battle = battle
        self.background = background
        self.reset()

    def reset(self):
        """Clear per-battle animation, turn, and message state for a fresh fight."""
        self.submenu = None
        self.attack_state = None
        self.attack_index = 0
        self.enemy_attack_state = None
        self.enemy_attack_timer = 0
        self.enemy_x = ENEMY_X
        self.luna_x = LUNA_X
        self.turn_steps = []
        self.step_index = 0
        self.step_started = False
        self.step_resolved = False
        self.step_time = 0
        self.round_finished = False
        self.turn_active = False
        self.enemy_hurt_until = 0
        self.luna_hurt_until = 0
        self.enemy_dodge_until = 0
        self.luna_dodge_until = 0
        self.effects.reset()
        self.death_start = None
        self.enemy_hp_display = float(self.battle.enemy.hp)
        self.luna_hp_display = float(self.battle.player_hp)
        self.focus_display = float(self.battle.focus)
        self.messages.reset()

    def draw(self):
        """Draw the battle screen: sprites, bars, message, and buttons."""
        self.screen.blit(self.background, (0, 0))
        now = pygame.time.get_ticks()
        self._update_animations(now)
        self._update_hp_tween()
        self._draw_luna(now)
        self._draw_enemy(now)

        draw_outlined_text(
            self.screen, self.small_font,
            f"Luna HP {self.battle.player_hp}/{self.battle.player_hp_max}", (40, 30),
        )
        draw_outlined_text(
            self.screen, self.small_font,
            f"{self.battle.enemy.name} HP {self.battle.enemy.hp}/{self.battle.enemy.max_hp}", (460, 30),
        )
        draw_outlined_text(
            self.screen, self.small_font,
            f"Focus {self.battle.focus}/{Battle.MAX_FOCUS}", (40, 80),
        )

        draw_bar(
            self.screen, self.small_font, 40, 60, 300, 20,
            int(self.luna_hp_display), self.battle.player_hp_max, COLOR_HP_BAR,
        )
        draw_bar(
            self.screen, self.small_font, 460, 60, 300, 20,
            int(self.enemy_hp_display), self.battle.enemy.max_hp, COLOR_HP_BAR,
        )
        if "night_vision" in self.battle.statuses and self.battle.enemy.intent:
            intent = self.battle.enemy.intent
            text = f"Intent: {intent['name']}"
            if "damage" in intent:
                text += f" ({intent['damage'][0]}-{intent['damage'][1]})"
            color = COLOR_WHITE if not intent.get("heavy") else COLOR_HEAVY
            draw_outlined_text(self.screen, self.small_font, text, (460, 90), color=color)
        draw_bar(
            self.screen, self.small_font, 40, 110, 300, 20,
            int(self.focus_display), Battle.MAX_FOCUS, COLOR_FOCUS_BAR,
        )

        self._draw_message(self.messages.lines())

        menu = self._battle_menu()
        hovered = None
        for button in menu["buttons"]:
            if menu["refresh"]:
                menu["refresh"](button)
            if menu["disabled"](button):
                draw_disabled_button(self.screen, button, menu["font"])
            else:
                button.draw(self.screen, menu["font"])
            if button.rect.collidepoint(pygame.mouse.get_pos()):
                hovered = menu["tooltip"](button)
        if menu["back"]:
            self.back_button.draw(self.screen, self.small_font)
        self._draw_tooltip(hovered)
        self.effects.draw_particles(self.screen, now)
        self.effects.draw_popups(self.screen, self.small_font, now)
        self.effects.apply_shake(self.screen, now)

    def handle_click(self, pos):
        """Handle clicks on the battle menu and its submenus."""
        if self.battle.phase != "player" or self.turn_active:
            return
        menu = self._battle_menu()
        if menu["back"] and self.back_button.rect.collidepoint(pos):
            self.submenu = None
        for button in menu["buttons"]:
            if button.rect.collidepoint(pos):
                hp_before = self.battle.player_hp
                focus_before = self.battle.focus
                menu["activate"](button)
                healed = self.battle.player_hp - hp_before
                if healed > 0:
                    self.effects.spawn_heal(healed, self.luna_x)
                gained = self.battle.focus - focus_before
                if gained > 0:
                    self.effects.spawn_focus(gained, self.luna_x)
                if menu["back"]:
                    self.submenu = None
        if not self.turn_active and self.battle.phase == "enemy":
            self._begin_turn(self.battle.plan_enemy_only())

    def update(self):
        """Resolve the current turn's steps; return True when the battle is over."""
        now = pygame.time.get_ticks()
        self.messages.sync(self.battle.message, now)
        self.messages.advance(now)
        if not self.turn_active:
            return False

        # A decided fight waits for the current swing and death animation.
        if self.battle.over:
            if self.battle.won:
                if self.death_start is None:
                    self.death_start = now
                    frames = self.assets.enemy_frames[self.battle.enemy.sprite]
                    self.effects.spawn_death_dust(
                        self.enemy_x, 360 + frames[0].get_height() // 2
                    )
                if (not self._luna_busy() and not self._enemy_busy()
                        and now - self.death_start >= DEATH_TIME):
                    self.turn_active = False
                    return True
            elif not self._luna_busy() and not self._enemy_busy():
                self.turn_active = False
                return True
            return False

        if self.step_index >= len(self.turn_steps):
            return self._end_turn(now)

        step = self.turn_steps[self.step_index]
        if step["actor"] == "luna":
            self._step_luna(now)
        else:
            self._step_enemy(now, step)
        return False

    def _update_animations(self, now):
        """Advance the cat and enemy animation frames based on elapsed time."""
        if self.attack_state == "walk_to":
            progress = min(1.0, (now - self.attack_timer) / WALK_TIME)
            self.luna_x = LUNA_X + (LUNA_ATTACK_X - LUNA_X) * progress
            if now - self.walk_timer > 100:
                self.walk_timer = now
                self.walk_index = (self.walk_index + 1) % len(self.assets.walk_frames)
            if progress >= 1.0:
                self.attack_state = "attacking"
                self.attack_index = 0
                self.attack_timer = now
        elif self.attack_state == "attacking":
            if now - self.attack_timer > 80:
                self.attack_timer = now
                self.attack_index += 1
                if self.attack_index >= len(self.assets.luna_attack_frames):
                    self.attack_state = "walk_back"
                    self.attack_timer = now
        elif self.attack_state == "walk_back":
            progress = min(1.0, (now - self.attack_timer) / WALK_TIME)
            self.luna_x = LUNA_ATTACK_X + (LUNA_X - LUNA_ATTACK_X) * progress
            if now - self.walk_timer > 100:
                self.walk_timer = now
                self.walk_index = (self.walk_index + 1) % len(self.assets.walk_frames)
            if progress >= 1.0:
                self.attack_state = None
                self.luna_x = LUNA_X
        elif now - self.anim_timer > 150:
            self.anim_timer = now
            self.anim_index = (self.anim_index + 1) % len(self.assets.luna_frames)
        if self.enemy_attack_state == "walk_to":
            progress = min(1.0, (now - self.enemy_attack_timer) / WALK_TIME)
            self.enemy_x = ENEMY_X + (ENEMY_ATTACK_X - ENEMY_X) * progress
            if progress >= 1.0:
                self.enemy_attack_state = "attacking"
                self.enemy_attack_timer = now
        elif self.enemy_attack_state == "attacking":
            if now - self.enemy_attack_timer > 200:
                self.enemy_attack_state = "walk_back"
                self.enemy_attack_timer = now
        elif self.enemy_attack_state == "walk_back":
            progress = min(1.0, (now - self.enemy_attack_timer) / WALK_TIME)
            self.enemy_x = ENEMY_ATTACK_X + (ENEMY_X - ENEMY_ATTACK_X) * progress
            if progress >= 1.0:
                self.enemy_attack_state = None
                self.enemy_x = ENEMY_X
        if now - self.enemy_anim_timer > 70:
            self.enemy_anim_timer = now
            self.enemy_anim_index = (self.enemy_anim_index + 1) % len(
                self.assets.enemy_frames[self.battle.enemy.sprite]
            )

    def _update_hp_tween(self):
        """Ease the drawn bars toward their true values so changes are visible."""
        self.luna_hp_display += (self.battle.player_hp - self.luna_hp_display) * TWEEN_RATE
        self.enemy_hp_display += (self.battle.enemy.hp - self.enemy_hp_display) * TWEEN_RATE
        self.focus_display += (self.battle.focus - self.focus_display) * TWEEN_RATE

    def _status_aura(self, frame, pos, statuses, now):
        """Draw a pulsing colored aura for a combatant's active statuses."""
        for key, color in STATUS_AURA:
            if key in statuses:
                break
        else:
            return
        t = (now % 600) / 600
        alpha = 35 + int(35 * (1 - abs(2 * t - 1)))
        self.effects.blit_flash(self.screen, frame, pos, color, alpha)

    def _draw_luna(self, now):
        """Draw Luna with her dodge hop, status aura, and hurt flash."""
        if self.attack_state == "attacking":
            frame = self.assets.luna_attack_frames[self.attack_index]
        elif self.attack_state in ("walk_to", "walk_back"):
            frame = self.assets.walk_frames[self.walk_index]
        else:
            frame = self.assets.luna_frames[self.anim_index]
        x, y = self.luna_x, 340
        if now < self.luna_hurt_until:
            x -= int(RECOIL * (self.luna_hurt_until - now) / HURT_TIME)
        dx, dy = self.effects.dodge_offset(now, self.luna_dodge_until, -1)
        x, y = x + dx, y + dy
        self.screen.blit(frame, (x, y))
        self._status_aura(frame, (x, y), self.battle.statuses, now)
        if now < self.luna_hurt_until:
            self.effects.blit_flash(
                self.screen, frame, (x, y), COLOR_WHITE,
                210 * (self.luna_hurt_until - now) / HURT_TIME,
            )

    def _draw_enemy(self, now):
        """Draw the enemy with dodge hop, status aura, flash, and death."""
        frames = self.assets.enemy_frames[self.battle.enemy.sprite]
        frame = frames[self.enemy_anim_index % len(frames)]
        if self.battle.over and self.battle.won and self.death_start is not None:
            if self._enemy_dying(now):
                self._draw_enemy_death(frame, now)
            return
        x = self.enemy_x - frame.get_width() // 2
        y = 360 - frame.get_height() // 2
        if now < self.enemy_hurt_until:
            x += int(RECOIL * (self.enemy_hurt_until - now) / HURT_TIME)
        dx, dy = self.effects.dodge_offset(now, self.enemy_dodge_until, 1)
        x, y = x + dx, y + dy
        self.screen.blit(frame, (x, y))
        if self.enemy_attack_state == "attacking":
            self.effects.blit_flash(self.screen, frame, (x, y), COLOR_HEAVY, 110)
        self._status_aura(frame, (x, y), self.battle.enemy.statuses, now)
        if now < self.enemy_hurt_until:
            self.effects.blit_flash(
                self.screen, frame, (x, y), COLOR_WHITE,
                210 * (self.enemy_hurt_until - now) / HURT_TIME,
            )

    def _enemy_dying(self, now):
        """Return True while the defeated enemy's death animation plays."""
        return (
            self.battle.over
            and self.battle.won
            and self.death_start is not None
            and now - self.death_start < DEATH_TIME
        )

    def _draw_enemy_death(self, frame, now):
        """Flash on the killing blow, then tip the enemy over as it fades."""
        progress = min(1.0, (now - self.death_start) / DEATH_TIME)
        if progress < 0.18:
            x = self.enemy_x - frame.get_width() // 2
            y = 360 - frame.get_height() // 2
            self.screen.blit(frame, (x, y))
            self.effects.blit_flash(self.screen, frame, (x, y), COLOR_WHITE, 220)
            return
        q = (progress - 0.18) / 0.82
        img = pygame.transform.rotate(frame, -70 * q)
        img.set_alpha(int(255 * (1 - q)))
        feet_y = 360 + frame.get_height() // 2 + int(12 * q)
        self.screen.blit(img, img.get_rect(midbottom=(self.enemy_x, feet_y)))

    def _battle_menu(self):
        """Return the active battle menu: its buttons and draw/click behavior."""
        if self.submenu == "instincts":
            return {
                "buttons": self.instinct_buttons,
                "font": self.small_font,
                "back": True,
                "disabled": lambda b: self.turn_active
                or not self.battle.can_use_instinct(b.action),
                "tooltip": lambda b: self.battle.INSTINCTS[b.action].get("desc"),
                "refresh": None,
                "activate": lambda b: self.battle.use_instinct(b.action),
            }
        if self.submenu == "items":
            return {
                "buttons": self.item_buttons,
                "font": self.small_font,
                "back": True,
                "disabled": lambda b: self.turn_active
                or not self.battle.can_use_item(b.action),
                "tooltip": lambda b: ITEMS[b.action].get("desc"),
                "refresh": lambda b: setattr(
                    b,
                    "text",
                    f"{ITEMS[b.action]['name']} x{self.battle.inventory[b.action]}",
                ),
                "activate": lambda b: self.battle.use_item(b.action),
            }
        return {
            "buttons": self.battle_buttons,
            "font": self.font,
            "back": False,
            "disabled": lambda b: self.turn_active
            or (b.action == "attack" and not self.battle.can_attack()),
            "tooltip": lambda b: None,
            "refresh": None,
            "activate": self._activate_battle_button,
        }

    def _activate_battle_button(self, button):
        """Queue the main battle menu's action for the turn sequencer."""
        if button.action == "attack":
            plan = self.battle.plan_attack()
            if plan is not None:
                self._begin_turn(plan)
        elif button.action == "rest":
            self.battle.rest()
        elif button.action == "defend":
            self.battle.defend()
        elif button.action == "items":
            self.submenu = "items"
        elif button.action == "instincts":
            self.submenu = "instincts"

    def _begin_turn(self, plan):
        """Store an ordered list of steps and start resolving them."""
        now = pygame.time.get_ticks()
        self.turn_steps = plan
        self.step_index = 0
        self.step_started = False
        self.step_resolved = False
        self.step_time = now
        self.round_finished = False
        self.turn_active = True

    def _next_step(self, now):
        """Advance to the next step in the turn."""
        self.step_index += 1
        self.step_started = False
        self.step_resolved = False
        self.step_time = now

    def _start_luna_attack(self, now):
        """Begin Luna's lunge animation."""
        self.attack_state = "walk_to"
        self.attack_index = 0
        self.attack_timer = now

    def _start_enemy_attack(self, now):
        """Begin the enemy's lunge animation."""
        self.enemy_attack_state = "walk_to"
        self.enemy_attack_timer = now

    def _luna_busy(self):
        """Return True while Luna's attack animation is playing."""
        return self.attack_state is not None

    def _enemy_busy(self):
        """Return True while the enemy's attack animation is playing."""
        return self.enemy_attack_state is not None

    def _draw_message(self, lines):
        """Draw the paged battle narration in one panel below the bars."""
        if not lines:
            return
        height = len(lines) * MESSAGE_LINE_SPACING + 16
        panel = pygame.Surface((MESSAGE_PANEL_WIDTH, height), pygame.SRCALPHA)
        rect = panel.get_rect()
        pygame.draw.rect(panel, (0, 0, 0, 130), rect, border_radius=10)
        pygame.draw.rect(panel, (255, 255, 255, 40), rect, width=2, border_radius=10)
        self.screen.blit(panel, (MESSAGE_PANEL_X, MESSAGE_PANEL_Y))
        y = MESSAGE_PANEL_Y + 8
        for line in lines:
            draw_outlined_text(
                self.screen, self.small_font, line,
                (MESSAGE_PANEL_X + 14, y), backing=False,
            )
            y += MESSAGE_LINE_SPACING
        if self.messages.has_more:
            draw_outlined_text(
                self.screen, self.small_font, "...",
                (MESSAGE_PANEL_X + MESSAGE_PANEL_WIDTH - 46, y - MESSAGE_LINE_SPACING),
                backing=False,
            )

    def _draw_tooltip(self, desc):
        """Draw a hover tooltip describing the submenu option under the cursor."""
        if not desc:
            return
        lines = wrap_lines([desc], self.small_font, MESSAGE_MAX_WIDTH)
        height = len(lines) * MESSAGE_LINE_SPACING + 16
        top = TOOLTIP_BOTTOM - height
        panel = pygame.Surface((MESSAGE_PANEL_WIDTH, height), pygame.SRCALPHA)
        rect = panel.get_rect()
        pygame.draw.rect(panel, (0, 0, 0, 130), rect, border_radius=10)
        pygame.draw.rect(panel, (255, 255, 255, 40), rect, width=2, border_radius=10)
        self.screen.blit(panel, (MESSAGE_PANEL_X, top))
        y = top + 8
        for line in lines:
            draw_outlined_text(
                self.screen, self.small_font, line,
                (MESSAGE_PANEL_X + 14, y), color=COLOR_HINT, backing=False,
            )
            y += MESSAGE_LINE_SPACING

    def _step_luna(self, now):
        """Animate Luna's attack and apply its damage at contact."""
        if not self.step_started:
            self._start_luna_attack(now)
            self.step_started = True
            self.step_resolved = False
        if not self.step_resolved and self.attack_state == "attacking":
            damage = self.battle.resolve_step(self.turn_steps[self.step_index])
            if damage > 0:
                self._after_hit(damage, on_enemy=True)
            else:
                self._dodge("enemy", now)
            self.step_resolved = True
        if self.attack_state is None:
            self._next_step(now)

    def _step_enemy(self, now, step):
        """Resolve the enemy's move, lunging and hitting at contact."""
        if not step["damage"]:
            # Status moves don't animate, but they still take the same wind-up
            # (and a short recovery) so the narration doesn't flash by.
            if not self.step_started:
                if now - self.step_time < ENEMY_DELAY:
                    return
                self.battle.resolve_step(step)
                self.step_started = True
                self.step_time = now
                return
            if now - self.step_time < WALK_TIME:
                return
            self._next_step(now)
            return
        if not self.step_started:
            if now - self.step_time < ENEMY_DELAY:
                return
            self._start_enemy_attack(now)
            self.step_started = True
            self.step_resolved = False
        if not self.step_resolved and self.enemy_attack_state == "attacking":
            before = self.battle.player_hp
            self.battle.resolve_step(step)
            dealt = before - self.battle.player_hp
            if dealt > 0:
                self._after_hit(
                    dealt,
                    on_enemy=False,
                    heavy=step["move"].get("heavy", False),
                )
            else:
                self._dodge("luna", now)
            self.step_resolved = True
        if self.enemy_attack_state is None:
            self._next_step(now)

    def _end_turn(self, now):
        """Finish the round, then pause so the player can read the narration."""
        if not self.round_finished:
            self.battle.finish_round()
            self.round_finished = True
            self.messages.sync(self.battle.message, now)
        if self.battle.over:
            self.turn_active = False
            return True
        if self.messages.read_out(now):
            self.turn_active = False
            self.round_finished = False
        return False

    def _after_hit(self, damage, on_enemy, heavy=False):
        """Trigger hit feedback for a landed blow."""
        now = pygame.time.get_ticks()
        if on_enemy:
            self.enemy_hurt_until = now + HURT_TIME
            self.effects.spawn_popup(f"-{damage}", self.enemy_x - 6, 300, COLOR_HEAVY)
        else:
            self.luna_hurt_until = now + HURT_TIME
            self.effects.spawn_popup(f"-{damage}", self.luna_x + 46, 300, COLOR_HP_BAR)
        if heavy:
            self.effects.shake(now)

    def _dodge(self, who, now):
        """React to a dodged attack: hop the target aside and show MISS."""
        if who == "enemy":
            self.enemy_dodge_until = now + DODGE_TIME
            self.effects.spawn_popup("MISS", self.enemy_x - 18, 300, COLOR_WHITE)
        else:
            self.luna_dodge_until = now + DODGE_TIME
            self.effects.spawn_popup("MISS", self.luna_x + 40, 300, COLOR_WHITE)
