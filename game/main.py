import asyncio
import threading

import pygame

from assets import Assets
from battle import Battle, ITEMS
from config import (
    BATTLE_BACKGROUNDS,
    COLOR_BLACK,
    COLOR_BUTTON,
    COLOR_END_BG,
    COLOR_FOCUS_BAR,
    COLOR_FOUND,
    COLOR_HEAVY,
    COLOR_HINT,
    COLOR_HP_BAR,
    COLOR_TITLE,
    COLOR_WHITE,
    ENEMY_ATTACK_X,
    ENEMY_DELAY,
    ENEMY_X,
    FONT,
    FOUND_NOTICE_TIME,
    LUNA_ATTACK_X,
    LUNA_X,
    MAP_BATTLE_DELAY,
    MAP_WALK_TIME,
    MESSAGE_MAX_WIDTH,
    VICTORY_IMAGE,
    WALK_TIME,
    WINDOW_SIZE,
)
from effects import DODGE_TIME, Effects
from messages import MessageLog
from music import Music
from run import BUILDINGS, DIFFICULTY_TIERS, Run
from story import SCENES, Story
from transitions import Transitions
from ui import (
    Button,
    draw_bar,
    draw_disabled_button,
    draw_outlined_text,
    wrap_lines,
)

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


class Game:
    """Main game loop, input handling, and drawing."""

    def __init__(self):
        """Set up pygame, load assets, and create the UI buttons."""
        pygame.init()
        self.music = Music()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Luna - a Hanover College Mystery")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT, 50)
        self.small_font = pygame.font.Font(FONT, 32)
        self.title_font = pygame.font.Font(FONT, 60)
        self.state = "menu"
        self.assets = Assets()
        self.battle_bg_current = self.assets.battle_bg
        self.transitions = Transitions()
        self.messages = MessageLog(self.small_font)

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
        self.effects = Effects()

        self.buttons = [
            Button(300, 250, 200, 60, "Start", "start"),
            Button(300, 330, 200, 60, "Quit", "quit"),
        ]
        self.difficulty_buttons = [
            Button(300, 190 + i * 75, 200, 60, name, tier)
            for i, (name, tier) in enumerate(DIFFICULTY_TIERS.items())
        ]
        self.difficulty_back = Button(300, 415, 200, 60, "Back", "back")
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
        self.menu_button = Button(300, 400, 200, 60, "Menu", "menu")
        self.seed_box = pygame.Rect(20, 540, 200, 40)
        self.seed_text = ""
        self.seed_focus = False

        self.map_buttons = [
            Button(560, 380, 120, 40, BUILDINGS[0]["name"], BUILDINGS[0]["name"]),
            Button(260, 135, 120, 40, BUILDINGS[1]["name"], BUILDINGS[1]["name"]),
            Button(260, 380, 120, 40, BUILDINGS[2]["name"], BUILDINGS[2]["name"]),
            Button(490, 550, 120, 40, BUILDINGS[3]["name"], BUILDINGS[3]["name"]),
        ]
        self.map_luna_pos = pygame.Vector2(160, 60)
        self.map_move = None
        self.map_arrive_timer = 0
        self.map_walk_index = 0
        self.map_walk_timer = 0
        self.pending_battle = None
        self.found_notice_start = None
        self.run_state = None
        self.battle = None

        self.story = None
        self.intro_start = 0
        self.skip_button = Button(660, 545, 120, 40, "Skip", "skip")
        self.music.play_title()
        try:
            threading.Thread(target=self._preload_scenes, daemon=True).start()
        except RuntimeError:
            pass

        self._click_handlers = {
            "menu": self._click_menu,
            "difficulty": self._click_difficulty,
            "intro": self._click_intro,
            "map": self._click_map,
            "battle": self._click_battle,
            "victory": self._click_end,
            "defeat": self._click_end,
        }
        self._draw_screens = {
            "menu": self.draw_menu,
            "difficulty": self.draw_difficulty,
            "intro": self.draw_intro,
            "map": self.draw_map,
            "battle": self.draw_battle,
            "victory": self._draw_victory,
            "defeat": self._draw_defeat,
        }
        self._update_screens = {
            "map": self.update_map,
            "battle": self.update_battle,
        }

    def _preload_scenes(self):
        """Load and scale every intro scene in the background at startup."""
        for scene in SCENES:
            self.assets.scene_image(scene["image"])

    def draw_menu(self):
        """Draw the title screen with background, title, and menu buttons."""
        self.screen.blit(self.assets.background, (0, 0))
        title = "Luna - a Hanover College Mystery"
        title_surface = self.title_font.render(title, True, COLOR_BLACK)
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 90))
        title_surface2 = self.title_font.render(title, True, COLOR_TITLE)
        title_rect2 = title_surface2.get_rect(
            center=(self.screen.get_width() // 2, 88), left=(title_rect.left + 2)
        )
        self.screen.blit(title_surface, title_rect)
        self.screen.blit(title_surface2, title_rect2)
        for button in self.buttons:
            button.draw(self.screen, self.font)
        draw_outlined_text(self.screen, self.small_font, "Seed (optional):", (20, 500))
        pygame.draw.rect(self.screen, COLOR_BUTTON, self.seed_box, border_radius=5)
        pygame.draw.rect(self.screen, COLOR_BLACK, self.seed_box, width=3, border_radius=5)
        label = self.seed_text if self.seed_text else "random"
        seed_surface = self.small_font.render(label, True, COLOR_WHITE)
        self.screen.blit(seed_surface, (self.seed_box.x + 8, self.seed_box.y + 4))

    def draw_difficulty(self):
        """Draw the difficulty selection screen with the seed preview."""
        self.screen.blit(self.assets.background, (0, 0))
        panel = pygame.Surface((300, 345), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 165), panel.get_rect(), border_radius=14)
        pygame.draw.rect(panel, (255, 255, 255, 90), panel.get_rect(), width=3,
                         border_radius=14)
        self.screen.blit(panel, (250, 158))
        label = "Choose difficulty"
        width = self.title_font.size(label)[0]
        draw_outlined_text(
            self.screen, self.title_font, label,
            ((WINDOW_SIZE[0] - width) // 2, 88),
        )
        for button in self.difficulty_buttons:
            button.draw(self.screen, self.font)
        self.difficulty_back.draw(self.screen, self.font)
        seed = self.seed_text if self.seed_text else "random"
        draw_outlined_text(self.screen, self.small_font, f"Seed: {seed}", (20, 540))

    def draw_map(self):
        """Draw the campus map with building choices and run status."""
        self.screen.blit(self.assets.campus_bg, (0, 0))
        draw_outlined_text(self.screen, self.title_font, "Choose a building", (430, 50))
        for button in self.map_buttons:
            if self.run_state.is_cleared(button.action):
                draw_disabled_button(self.screen, button, self.small_font)
            elif (
                self.run_state.found_human
                and button.action == self.run_state.human_building
            ):
                button.draw(self.screen, self.small_font, text_color=COLOR_TITLE)
            else:
                button.draw(self.screen, self.small_font)
        if (
            self.found_notice_start is not None
            and pygame.time.get_ticks() - self.found_notice_start < FOUND_NOTICE_TIME
        ):
            notice = "You found Oxiel - the Campus Guardian stands in the way."
            width = self.small_font.size(notice)[0]
            draw_outlined_text(
                self.screen, self.small_font, notice,
                ((WINDOW_SIZE[0] - width) // 2, 105), color=COLOR_FOUND,
            )
        draw_outlined_text(
            self.screen, self.small_font,
            f"Seed: {self.run_state.seed}", (40, 500),
        )
        draw_outlined_text(
            self.screen, self.small_font,
            f"HP {self.run_state.player_hp}/{self.run_state.player_hp_max}   Focus {self.run_state.focus}",
            (40, 540),
        )
        if self.run_state.last_reward:
            draw_outlined_text(
                self.screen, self.small_font,
                f"Reward: +1 {ITEMS[self.run_state.last_reward]['name']}",
                (40, 570), color=COLOR_TITLE,
            )
        if self.map_move is not None:
            frame = self.assets.map_walk_frames[self.map_walk_index]
        else:
            frame = self.assets.map_idle_frames[self.anim_index]
        self.screen.blit(frame, (self.map_luna_pos.x - frame.get_width() // 2,
                                 self.map_luna_pos.y - frame.get_height() // 2))

    def _battle_background_for(self, name):
        """Return the scaled background for the upcoming fight at a building."""
        if name is None:
            return self.assets.battle_bg
        spec = BATTLE_BACKGROUNDS.get(name)
        if not spec:
            return self.assets.battle_bg
        stage = self.run_state.stage.get(name, 0)
        key = "guard" if stage == 0 else "boss" if stage == 1 else "final"
        return self.assets.battle_backgrounds.get(spec.get(key), self.assets.battle_bg)

    def _start_battle_for(self, name):
        """Start the battle for a building once Luna reaches it."""
        self.battle = self.run_state.start_battle(name)
        self.battle_bg_current = self._battle_background_for(name)
        self._reset_battle()
        self.state = "battle"

    def _is_final_boss(self, name):
        """Return True when the upcoming fight at name is the Campus Guardian."""
        return (
            name is not None
            and name == self.run_state.human_building
            and self.run_state.stage.get(name, 0) >= 2
        )

    def update_map(self):
        """Advance Luna's walk to the chosen building on the campus map."""
        now = pygame.time.get_ticks()
        if self.map_move is not None:
            start, end, start_time, duration = self.map_move
            progress = min(1.0, (now - start_time) / duration)
            if now - self.map_walk_timer > 90:
                self.map_walk_timer = now
                self.map_walk_index = (self.map_walk_index + 1) % len(self.assets.map_walk_frames)
            self.map_luna_pos = start.lerp(end, progress)
            if progress >= 1.0:
                self.map_move = None
                self.map_arrive_timer = now
                self.music.play_battle(boss=self._is_final_boss(self.pending_battle))
            return
        if self.pending_battle is not None and now - self.map_arrive_timer > MAP_BATTLE_DELAY:
            name, self.pending_battle = self.pending_battle, None
            self.transitions.start_spiral(
                lambda: self.transitions.start_wipe(
                    lambda: self._start_battle_for(name),
                    self.screen,
                    from_surface=self.transitions.black_surface,
                )
            )
            return
        if now - self.anim_timer > 200:
            self.anim_timer = now
            self.anim_index = (self.anim_index + 1) % len(self.assets.map_idle_frames)

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

    def draw_battle(self):
        """Draw the battle screen: sprites, bars, message, and buttons."""
        self.screen.blit(self.battle_bg_current, (0, 0))
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

    def draw_end(self, message, background=None):
        """Draw the victory or defeat screen with a back-to-menu button."""
        if background is None:
            self.screen.fill(COLOR_END_BG)
        else:
            self.screen.blit(background, (0, 0))
        text_w = self.title_font.size(message)[0]
        draw_outlined_text(
            self.screen, self.title_font, message,
            ((WINDOW_SIZE[0] - text_w) // 2, 240),
        )
        self.menu_button.draw(self.screen, self.font)

    def draw_intro(self):
        """Draw the current intro scene: image, revealed line, and skip button."""
        scene = self.story.scene() if self.story else None
        if scene is None:
            return
        self.screen.blit(self.assets.scene_image(scene["image"]), (0, 0))
        elapsed = pygame.time.get_ticks() - self.intro_start
        line = self.story.visible_line(elapsed)
        if line:
            wrapped = wrap_lines([line], self.small_font, MESSAGE_MAX_WIDTH)
            y = 430
            for part in wrapped:
                width = self.small_font.size(part)[0]
                draw_outlined_text(
                    self.screen, self.small_font, part,
                    ((WINDOW_SIZE[0] - width) // 2, y),
                )
                y += 36
        if self.story.reveal_done(elapsed):
            hint = "click to continue"
            width = self.small_font.size(hint)[0]
            draw_outlined_text(
                self.screen, self.small_font, hint,
                ((WINDOW_SIZE[0] - width) // 2, 545), color=COLOR_HINT,
            )
        self.skip_button.draw(self.screen, self.small_font)

    def _preload_scene(self):
        """Load the current intro scene image while the screen is black."""
        scene = self.story.scene() if self.story else None
        if scene:
            self.assets.scene_image(scene["image"])

    def _begin_intro(self):
        """Create a fresh intro and switch to it, called at full black."""
        self.story = Story()
        self.intro_start = pygame.time.get_ticks()
        self.state = "intro"
        self._preload_scene()

    def _intro_advance(self):
        """Snap the current scene to its last line, or move to the next."""
        now = pygame.time.get_ticks()
        elapsed = now - self.intro_start
        if not self.story.reveal_done(elapsed):
            self.intro_start = now - self.story.snap()
        else:
            self._advance_intro()

    def _advance_intro(self):
        """Fade to the next scene, or to the map after the final scene."""
        def at_black():
            if not self.story.advance():
                self.state = "map"
            else:
                self._preload_scene()
                self.intro_start = pygame.time.get_ticks()

        self.transitions.start_fade(at_black)

    def _skip_intro(self):
        """Fade straight to the map."""
        self.transitions.start_fade(self._enter_map)

    def _enter_map(self):
        """Switch to the campus map, called at full black."""
        self.state = "map"

    def handle_click(self, pos):
        """Route a mouse click to the current screen's handler."""
        if self.transitions.busy:
            return
        handler = self._click_handlers.get(self.state)
        if handler:
            handler(pos)

    def _click_menu(self, pos):
        """Handle clicks on the title screen."""
        if self.seed_box.collidepoint(pos):
            self.seed_focus = True
        else:
            self.seed_focus = False
        for button in self.buttons:
            if button.rect.collidepoint(pos):
                if button.action == "start":
                    self.state = "difficulty"
                elif button.action == "quit":
                    self.running = False

    def _click_difficulty(self, pos):
        """Start a run at the chosen difficulty, or go back to the title."""
        if self.difficulty_back.rect.collidepoint(pos):
            self.state = "menu"
            return
        for button in self.difficulty_buttons:
            if button.rect.collidepoint(pos):
                self._start_run(button.action)
                return

    def _start_run(self, tier):
        """Create a run at the given difficulty and fade into the intro."""
        seed = int(self.seed_text) if self.seed_text.isdigit() else None
        self.run_state = Run(seed=seed, tier=tier)
        self.map_luna_pos = pygame.Vector2(400, 70)
        self.map_move = None
        self.map_arrive_timer = 0
        self.pending_battle = None
        self.found_notice_start = None
        self.music.play_campus()
        self.transitions.start_fade(self._begin_intro)

    def _click_intro(self, pos):
        """Advance the intro, or skip it when the skip button is clicked."""
        if self.skip_button.rect.collidepoint(pos):
            self._skip_intro()
        else:
            self._intro_advance()

    def _click_map(self, pos):
        """Start walking Luna to a chosen building."""
        if self.map_move is not None:
            return
        for button in self.map_buttons:
            if button.rect.collidepoint(pos) and not self.run_state.is_cleared(button.action):
                target_y = button.rect.centery + 50
                if target_y > WINDOW_SIZE[1] - 30:
                    target_y = button.rect.centery - 50
                self.map_move = (
                    self.map_luna_pos.copy(),
                    pygame.Vector2(button.rect.centerx, target_y),
                    pygame.time.get_ticks(),
                    MAP_WALK_TIME,
                )
                self.pending_battle = button.action
                self.map_walk_index = 0
                self.map_walk_timer = 0

    def _click_battle(self, pos):
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

    def _click_end(self, pos):
        """Return to the title screen from victory or defeat."""
        if self.menu_button.rect.collidepoint(pos):
            self.state = "menu"
            self.music.play_title()

    def _reset_battle(self):
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

    def _finish_battle(self):
        """Record the battle result in the run and pick the next screen."""
        self.run_state.end_battle(self.battle)
        if self.run_state.lost:
            self.state = "defeat"
            self.music.play_defeat()
        elif self.run_state.won:
            self.state = "victory"
            self.music.play_victory()
        else:
            self.state = "map"
            if self.run_state.found_human and self.found_notice_start is None:
                self.found_notice_start = pygame.time.get_ticks()
            self.music.play_campus()

    def update_battle(self):
        """Resolve the current turn's steps, applying hits at contact."""
        now = pygame.time.get_ticks()
        self.messages.sync(self.battle.message, now)
        self.messages.advance(now)
        if not self.turn_active:
            return

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
                    self._finish_battle()
            elif not self._luna_busy() and not self._enemy_busy():
                self.turn_active = False
                self._finish_battle()
            return

        if self.step_index >= len(self.turn_steps):
            self._end_turn(now)
            return

        step = self.turn_steps[self.step_index]
        if step["actor"] == "luna":
            self._step_luna(now)
        else:
            self._step_enemy(now, step)

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
            self._finish_battle()
            return
        if self.messages.read_out(now):
            self.turn_active = False
            self.round_finished = False

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

    def frame(self):
        """Process input and draw one frame of the game."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.music.handle_event(event)
            if event.type == pygame.KEYDOWN and self.seed_focus:
                if event.key == pygame.K_BACKSPACE:
                    self.seed_text = self.seed_text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.seed_focus = False
                elif event.unicode.isdigit():
                    self.seed_text += event.unicode
            if event.type == pygame.KEYDOWN and self.state == "intro":
                if not self.transitions.fade_active:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                        self._intro_advance()
                    elif event.key == pygame.K_ESCAPE:
                        self._skip_intro()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
        self._draw_screens[self.state]()
        update = self._update_screens.get(self.state)
        if update:
            update()
        self.transitions.draw(self.screen)
        pygame.display.flip()

    def _draw_victory(self):
        """Draw the victory screen over the ending artwork."""
        self.draw_end(
            "Luna found Oxiel!",
            self.assets.scene_image(VICTORY_IMAGE),
        )

    def _draw_defeat(self):
        """Draw the defeat screen over Luna's box pose."""
        self.draw_end("Luna was defeated.", self.assets.defeat_background)

    def run(self):
        """Run the main loop: handle events, draw the state, flip the display."""
        self.running = True
        while self.running:
            self.frame()
            self.clock.tick(60)
        pygame.quit()


def main():
    """Desktop entry point."""
    Game().run()


async def web_main():
    """Browser entry point for pygodide: yields to the browser each frame."""
    game = Game()
    game.running = True
    clock = pygame.time.Clock()
    while game.running:
        game.frame()
        clock.tick(60)
        await asyncio.sleep(1 / 120)
    pygame.quit()


if __name__ == "__main__":
    main()
