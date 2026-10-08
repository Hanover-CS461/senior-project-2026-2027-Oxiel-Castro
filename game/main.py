import asyncio
import math
import re
import sys

import pygame

from battle import Battle, ITEMS
from run import BUILDINGS, Run
from config import (
    ATTACK_FRAMES,
    COLOR_BATTLE_BG,
    COLOR_END_BG,
    COLOR_FOCUS_BAR,
    COLOR_HP_BAR,
    COLOR_TITLE,
    DIFFICULTY_COLORS,
    DIFFICULTY_LABELS,
    ENEMY_DELAY,
    ENEMY_SPRITES,
    FADE_TIME,
    FONT,
    LUNA_ATTACK_X,
    LUNA_FRAMES,
    LUNA_X,
    MAP_BATTLE_DELAY,
    MAP_WALK_TIME,
    MESSAGE_MAX_WIDTH,
    MESSAGE_PAGE_LINES,
    READ_DELAY,
    WALK_FRAMES,
    WALK_TIME,
    WINDOW_SIZE,
    WIPE_TIME,
    COLOR_WHITE,
)
from sprites import load_frames
from story import Story
from ui import Button, draw_bar, draw_disabled_button, draw_outlined_text


class Game:
    """Main game loop, input handling, and drawing."""

    def __init__(self):
        """Set up pygame, load assets, and create the UI buttons."""
        pygame.init()
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("game/assets/music/POL-chubby-cat.wav")
            pygame.mixer.music.play(loops=-1)
        except pygame.error:
            pass
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Luna - a Hanover College Mystery")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT, 50)
        self.small_font = pygame.font.Font(FONT, 32)
        self.title_font = pygame.font.Font(FONT, 60)
        self.state = "menu"

        self.background = pygame.image.load("game/assets/images/background.png").convert()
        self.background = pygame.transform.scale(self.background, WINDOW_SIZE)
        self.battle_bg = pygame.image.load("game/assets/images/battle_bg.png").convert()
        self.battle_bg = pygame.transform.scale(self.battle_bg, WINDOW_SIZE)
        self.campus_bg = pygame.image.load("game/assets/images/campus.png").convert()
        self.campus_bg = pygame.transform.scale(self.campus_bg, WINDOW_SIZE)

        self.luna_frames = load_frames(
            "game/assets/images/Luna2.png", LUNA_FRAMES, size=(132, 96)
        )
        self.walk_frames = load_frames(
            "game/assets/images/Luna2.png", WALK_FRAMES, scale=5
        )
        self.enemy_frames = {
            key: load_frames(
                spec["path"], spec["frames"], scale=spec["scale"],
                flip=(key == "fly"), normalize=True,
            )
            for key, spec in ENEMY_SPRITES.items()
        }
        self.luna_attack_frames = load_frames(
            "game/assets/images/Luna2.png", ATTACK_FRAMES, scale=5
        )
        self.map_idle_frames = load_frames(
            "game/assets/images/Luna2.png", LUNA_FRAMES, scale=2
        )
        self.map_walk_frames = load_frames(
            "game/assets/images/Luna2.png", WALK_FRAMES, scale=2
        )

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

        self.buttons = [
            Button(300, 250, 200, 60, "Start", "start"),
            Button(300, 330, 200, 60, "Quit", "quit"),
        ]
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
        self.building_button = None
        self.map_luna_pos = pygame.Vector2(160, 60)
        self.map_move = None
        self.map_arrive_timer = 0
        self.map_walk_index = 0
        self.map_walk_timer = 0
        self.pending_battle = None
        self.run_state = None
        self.battle = None
        self.enemy_phase = False
        self.enemy_timer = 0
        self._message_pages = []
        self._message_page = 0
        self._message_timer = 0
        self._last_message = None

        self.story = None
        self.intro_start = 0
        self.skip_button = Button(660, 545, 120, 40, "Skip", "skip")
        self.fade_phase = None
        self.fade_start = 0
        self.fade_next = None
        self.fade_surface = pygame.Surface(WINDOW_SIZE)
        self.fade_surface.fill((0, 0, 0))
        self.wipe = None
        self._scene_cache = {}

    def draw_menu(self):
        """Draw the title screen with background, title, and menu buttons."""
        self.screen.blit(self.background, (0, 0))
        title = "Luna - a Hanover College Mystery"
        title_surface = self.title_font.render(title, True, (0, 0, 0))
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
        pygame.draw.rect(self.screen, (30, 144, 255), self.seed_box, border_radius=5)
        pygame.draw.rect(self.screen, (0, 0, 0), self.seed_box, width=3, border_radius=5)
        label = self.seed_text if self.seed_text else "random"
        seed_surface = self.small_font.render(label, True, (255, 255, 255))
        self.screen.blit(seed_surface, (self.seed_box.x + 8, self.seed_box.y + 4))

    def draw_map(self):
        """Draw the campus map with building choices and run status."""
        self.screen.blit(self.campus_bg, (0, 0))
        draw_outlined_text(self.screen, self.title_font, "Choose a building", (430, 50))
        for button in self.map_buttons:
            if self.run_state.is_cleared(button.action):
                draw_disabled_button(self.screen, button, self.small_font)
            else:
                button.draw(self.screen, self.small_font)
            tier = self.run_state.building_by_name(button.action)["tier"]
            label = DIFFICULTY_LABELS[tier]
            y = button.rect.centery - self.small_font.size(label)[1] // 2
            draw_outlined_text(
                self.screen, self.small_font, label,
                (button.rect.right + 10, y), color=DIFFICULTY_COLORS[tier],
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
            frame = self.map_walk_frames[self.map_walk_index]
        else:
            frame = self.map_idle_frames[self.anim_index]
        self.screen.blit(frame, (self.map_luna_pos.x - frame.get_width() // 2,
                                 self.map_luna_pos.y - frame.get_height() // 2))

    def _start_battle_for(self, name):
        """Start the battle for a building once Luna reaches it."""
        self.battle = self.run_state.start_battle(name)
        self._reset_battle()
        self.state = "battle"

    def update_map(self):
        """Advance Luna's walk to the chosen building on the campus map."""
        now = pygame.time.get_ticks()
        if self.map_move is not None:
            start, end, start_time, duration = self.map_move
            progress = min(1.0, (now - start_time) / duration)
            if now - self.map_walk_timer > 90:
                self.map_walk_timer = now
                self.map_walk_index = (self.map_walk_index + 1) % len(self.map_walk_frames)
            self.map_luna_pos = start.lerp(end, progress)
            if progress >= 1.0:
                self.map_move = None
                self.map_arrive_timer = now
            return
        if self.pending_battle is not None and now - self.map_arrive_timer > MAP_BATTLE_DELAY:
            name, self.pending_battle = self.pending_battle, None
            self._start_wipe(lambda: self._start_battle_for(name))
            return
        if now - self.anim_timer > 200:
            self.anim_timer = now
            self.anim_index = (self.anim_index + 1) % len(self.map_idle_frames)

    def _update_animations(self, now):
        """Advance the cat and enemy animation frames based on elapsed time."""
        if self.attack_state == "walk_to":
            progress = min(1.0, (now - self.attack_timer) / WALK_TIME)
            self.luna_x = LUNA_X + (LUNA_ATTACK_X - LUNA_X) * progress
            if now - self.walk_timer > 100:
                self.walk_timer = now
                self.walk_index = (self.walk_index + 1) % len(self.walk_frames)
            if progress >= 1.0:
                self.attack_state = "attacking"
                self.attack_index = 0
                self.attack_timer = now
        elif self.attack_state == "attacking":
            if now - self.attack_timer > 80:
                self.attack_timer = now
                self.attack_index += 1
                if self.attack_index >= len(self.luna_attack_frames):
                    self.attack_state = "walk_back"
                    self.attack_timer = now
        elif self.attack_state == "walk_back":
            progress = min(1.0, (now - self.attack_timer) / WALK_TIME)
            self.luna_x = LUNA_ATTACK_X + (LUNA_X - LUNA_ATTACK_X) * progress
            if now - self.walk_timer > 100:
                self.walk_timer = now
                self.walk_index = (self.walk_index + 1) % len(self.walk_frames)
            if progress >= 1.0:
                self.attack_state = None
                self.luna_x = LUNA_X
        elif now - self.anim_timer > 150:
            self.anim_timer = now
            self.anim_index = (self.anim_index + 1) % len(self.luna_frames)
        if now - self.enemy_anim_timer > 70:
            self.enemy_anim_timer = now
            self.enemy_anim_index = (self.enemy_anim_index + 1) % len(
                self.enemy_frames[self.battle.enemy.sprite]
            )

    def draw_battle(self):
        """Draw the battle screen: sprites, bars, message, and buttons."""
        self.screen.blit(self.battle_bg, (0, 0))
        self._update_animations(pygame.time.get_ticks())
        if self.attack_state == "attacking":
            luna = self.luna_attack_frames[self.attack_index]
        elif self.attack_state in ("walk_to", "walk_back"):
            luna = self.walk_frames[self.walk_index]
        else:
            luna = self.luna_frames[self.anim_index]
        self.screen.blit(luna, (self.luna_x, 340))
        enemy_frames = self.enemy_frames[self.battle.enemy.sprite]
        enemy = enemy_frames[self.enemy_anim_index % len(enemy_frames)]
        self.screen.blit(enemy, (620 - enemy.get_width() // 2, 360 - enemy.get_height() // 2))

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
            self.battle.player_hp, self.battle.player_hp_max, COLOR_HP_BAR,
        )
        draw_bar(
            self.screen, self.small_font, 460, 60, 300, 20,
            self.battle.enemy.hp, self.battle.enemy.max_hp, COLOR_HP_BAR,
        )
        if "night_vision" in self.battle.statuses and self.battle.enemy.intent:
            intent = self.battle.enemy.intent
            text = f"Intent: {intent['name']}"
            if "damage" in intent:
                text += f" ({intent['damage'][0]}-{intent['damage'][1]})"
            color = COLOR_WHITE if not intent.get("heavy") else (255, 200, 0)
            draw_outlined_text(self.screen, self.small_font, text, (460, 90), color=color)
        draw_bar(
            self.screen, self.small_font, 40, 110, 300, 20,
            self.battle.focus, Battle.MAX_FOCUS, COLOR_FOCUS_BAR,
        )

        lines = (
            self._message_pages[self._message_page]
            if self._message_pages
            else [self.battle.message]
        )
        y = 130
        for line in lines:
            draw_outlined_text(self.screen, self.small_font, line, (40, y))
            y += 36
        if len(self._message_pages) > self._message_page + 1:
            draw_outlined_text(self.screen, self.small_font, "...", (40, y))

        if self.submenu == "instincts":
            for button in self.instinct_buttons:
                disabled = self.enemy_phase or not self.battle.can_use_instinct(button.action)
                if disabled:
                    draw_disabled_button(self.screen, button, self.small_font)
                else:
                    button.draw(self.screen, self.small_font)
            self.back_button.draw(self.screen, self.small_font)
        elif self.submenu == "items":
            for button in self.item_buttons:
                name = button.action
                button.text = f"{ITEMS[name]['name']} x{self.battle.inventory[name]}"
                disabled = self.enemy_phase or not self.battle.can_use_item(name)
                if disabled:
                    draw_disabled_button(self.screen, button, self.small_font)
                else:
                    button.draw(self.screen, self.small_font)
            self.back_button.draw(self.screen, self.small_font)
        else:
            for button in self.battle_buttons:
                disabled = self.enemy_phase or (
                    button.action == "attack" and not self.battle.can_attack()
                )
                if disabled:
                    draw_disabled_button(self.screen, button, self.font)
                else:
                    button.draw(self.screen, self.font)

    def draw_end(self, message):
        """Draw the victory or defeat screen with a back-to-menu button."""
        self.screen.fill(COLOR_END_BG)
        text = self.title_font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(400, 250))
        self.screen.blit(text, text_rect)
        self.menu_button.draw(self.screen, self.font)

    def draw_intro(self):
        """Draw the current intro scene: image, revealed line, and skip button."""
        scene = self.story.scene() if self.story else None
        if scene is None:
            return
        self.screen.blit(self._scene_image(scene["image"]), (0, 0))
        elapsed = pygame.time.get_ticks() - self.intro_start
        line = self.story.visible_line(elapsed)
        if line:
            wrapped = self._wrap_lines([line], self.small_font, MESSAGE_MAX_WIDTH)
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
                ((WINDOW_SIZE[0] - width) // 2, 545), color=(200, 200, 200),
            )
        self.skip_button.draw(self.screen, self.small_font)

    def _scene_image(self, path):
        """Load and cache a scene image, falling back to the menu background."""
        if path in self._scene_cache:
            return self._scene_cache[path]
        image = self.background
        try:
            loaded = pygame.image.load(path).convert()
            image = pygame.transform.scale(loaded, WINDOW_SIZE)
        except (pygame.error, FileNotFoundError, TypeError):
            image = self.background
        self._scene_cache[path] = image
        return image

    def _start_fade(self, next_action):
        """Begin a through-black fade, running next_action at full black."""
        if self.fade_phase is not None:
            return
        self.fade_phase = "out"
        self.fade_start = pygame.time.get_ticks()
        self.fade_next = next_action

    def _draw_fade(self):
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
            self.screen.blit(self.fade_surface, (0, 0))

    def _begin_intro(self):
        """Create a fresh intro and switch to it, called at full black."""
        self.story = Story()
        self.intro_start = pygame.time.get_ticks()
        self.state = "intro"

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
                self.intro_start = pygame.time.get_ticks()

        self._start_fade(at_black)

    def _skip_intro(self):
        """Fade straight to the map."""
        self._start_fade(self._enter_map)

    def _enter_map(self):
        """Switch to the campus map, called at full black."""
        self.state = "map"

    def _start_wipe(self, next_action):
        """Begin a rotating radial wipe, running next_action immediately."""
        self.wipe = {
            "from": self.screen.copy(),
            "start": pygame.time.get_ticks(),
            "center": (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2),
            "radius": 540,
            "start_angle": -90,
        }
        next_action()

    def _wedge_points(self, swept):
        """Return the polygon points of a pie wedge swept by degrees."""
        cx, cy = self.wipe["center"]
        radius = self.wipe["radius"]
        start = self.wipe["start_angle"]
        steps = max(1, int(swept / 6))
        points = [(cx, cy)]
        for i in range(steps + 1):
            angle = math.radians(start + swept * i / steps)
            points.append(
                (int(cx + radius * math.cos(angle)),
                 int(cy + radius * math.sin(angle)))
            )
        return points

    def _draw_wipe(self):
        """Reveal the current screen through a growing, rotating wedge."""
        if self.wipe is None:
            return
        now = pygame.time.get_ticks()
        progress = min(1.0, (now - self.wipe["start"]) / WIPE_TIME)
        mask = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        mask.fill((255, 255, 255, 255))
        points = self._wedge_points(progress * 360.0)
        if len(points) >= 3:
            pygame.draw.polygon(mask, (255, 255, 255, 0), points)
        layer = self.wipe["from"].convert_alpha()
        layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(layer, (0, 0))
        if progress >= 1.0:
            self.wipe = None

    def handle_click(self, pos):
        """Route a mouse click to the current screen's buttons."""
        if self.fade_phase is not None or self.wipe is not None:
            return
        if self.state == "menu":
            if self.seed_box.collidepoint(pos):
                self.seed_focus = True
            else:
                self.seed_focus = False
            for button in self.buttons:
                if button.rect.collidepoint(pos):
                    if button.action == "start":
                        seed = int(self.seed_text) if self.seed_text.isdigit() else None
                        self.run_state = Run(seed=seed)
                        self.map_luna_pos = pygame.Vector2(400, 70)
                        self.map_move = None
                        self.map_arrive_timer = 0
                        self.pending_battle = None
                        self._start_fade(self._begin_intro)
                    elif button.action == "quit":
                        self.running = False
        elif self.state == "intro":
            if self.skip_button.rect.collidepoint(pos):
                self._skip_intro()
            else:
                self._intro_advance()
        elif self.state == "map":
            if self.map_move is not None:
                return
            for button in self.map_buttons:
                if button.rect.collidepoint(pos) and not self.run_state.is_cleared(button.action):
                    self.map_move = (
                        self.map_luna_pos.copy(),
                        pygame.Vector2(button.rect.centerx, button.rect.centery + 50),
                        pygame.time.get_ticks(),
                        MAP_WALK_TIME,
                    )
                    self.pending_battle = button.action
                    self.map_walk_index = 0
                    self.map_walk_timer = 0
        elif self.state == "battle":
            if self.battle.phase == "player" and not self.enemy_phase:
                if self.submenu == "instincts":
                    if self.back_button.rect.collidepoint(pos):
                        self.submenu = None
                    for button in self.instinct_buttons:
                        if button.rect.collidepoint(pos):
                            self.battle.use_instinct(button.action)
                            self.submenu = None
                elif self.submenu == "items":
                    if self.back_button.rect.collidepoint(pos):
                        self.submenu = None
                    for button in self.item_buttons:
                        if button.rect.collidepoint(pos):
                            self.battle.use_item(button.action)
                            self.submenu = None
                else:
                    for button in self.battle_buttons:
                        if button.rect.collidepoint(pos):
                            if button.action == "attack":
                                self.battle.attack()
                                if self.battle.luna_attacked:
                                    self.attack_state = "walk_to"
                                    self.attack_index = 0
                                    self.attack_timer = pygame.time.get_ticks()
                                    self.battle.luna_attacked = False
                            elif button.action == "rest":
                                self.battle.rest()
                            elif button.action == "defend":
                                self.battle.defend()
                            elif button.action == "items":
                                self.submenu = "items"
                            elif button.action == "instincts":
                                self.submenu = "instincts"
                if self.battle.over:
                    self._finish_battle()
                elif self.battle.phase == "enemy":
                    self.enemy_phase = True
                    self.enemy_timer = pygame.time.get_ticks()
        elif self.state in ("victory", "defeat"):
            if self.menu_button.rect.collidepoint(pos):
                self.state = "menu"

    def _reset_battle(self):
        """Clear per-battle animation and message state for a fresh fight."""
        self.enemy_phase = False
        self.enemy_timer = 0
        self.submenu = None
        self.attack_state = None
        self.attack_index = 0
        self._message_pages = []
        self._message_page = 0
        self._message_timer = 0
        self._last_message = None

    def _finish_battle(self):
        """Record the battle result in the run and pick the next screen."""
        self.run_state.end_battle(self.battle)
        if self.run_state.lost:
            self.state = "defeat"
        elif self.run_state.won:
            self.state = "victory"
        else:
            self.state = "map"

    def _message_sentences(self, msg):
        """Split a battle message into its individual narration sentences."""
        return [s for s in re.split(r"(?<=[.!])\s+", msg) if s]

    def _wrap_lines(self, sentences, font, max_width):
        """Word-wrap sentences into lines that fit within max_width."""
        lines = []
        for sentence in sentences:
            current = ""
            for word in sentence.split():
                trial = f"{current} {word}".strip()
                if font.size(trial)[0] <= max_width:
                    current = trial
                else:
                    lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines

    def _sync_message(self, now):
        """Rebuild the paged message log whenever the battle message changes."""
        msg = self.battle.message
        if msg == self._last_message:
            return
        self._last_message = msg
        sentences = self._message_sentences(msg)
        lines = self._wrap_lines(sentences, self.small_font, MESSAGE_MAX_WIDTH)
        self._message_pages = [
            lines[i : i + MESSAGE_PAGE_LINES]
            for i in range(0, len(lines), MESSAGE_PAGE_LINES)
        ]
        self._message_page = 0
        self._message_timer = now

    def _advance_message(self, now):
        """Advance to the next page of the message log after a pause."""
        if (
            self._message_page < len(self._message_pages) - 1
            and now - self._message_timer > READ_DELAY
        ):
            self._message_page += 1
            self._message_timer = now

    def _message_done(self):
        """Return True once the final message page is being shown."""
        return not self._message_pages or self._message_page >= len(self._message_pages) - 1

    def update_battle(self):
        """Run the enemy turn, page through messages, then let the player act."""
        now = pygame.time.get_ticks()
        self._sync_message(now)
        if not self.enemy_phase:
            return
        if self.battle.phase == "enemy":
            if now - self.enemy_timer > ENEMY_DELAY:
                self.battle.enemy_turn()
                self.enemy_timer = now
                if self.battle.luna_attacked:
                    self.attack_state = "walk_to"
                    self.attack_index = 0
                    self.attack_timer = pygame.time.get_ticks()
                    self.battle.luna_attacked = False
                if self.battle.over:
                    self._finish_battle()
        elif self._message_done() and now - self._message_timer > READ_DELAY:
            self.enemy_phase = False
        else:
            self._advance_message(now)

    def frame(self):
        """Process input and draw one frame of the game."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and self.seed_focus:
                if event.key == pygame.K_BACKSPACE:
                    self.seed_text = self.seed_text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.seed_focus = False
                elif event.unicode.isdigit():
                    self.seed_text += event.unicode
            if event.type == pygame.KEYDOWN and self.state == "intro":
                if self.fade_phase is None:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                        self._intro_advance()
                    elif event.key == pygame.K_ESCAPE:
                        self._skip_intro()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "intro":
            self.draw_intro()
        elif self.state == "map":
            self.draw_map()
            self.update_map()
        elif self.state == "battle":
            self.draw_battle()
            self.update_battle()
        elif self.state == "victory":
            self.draw_end("Luna found Oxiel!")
        elif self.state == "defeat":
            self.draw_end("Luna was defeated.")
        self._draw_wipe()
        self._draw_fade()
        pygame.display.flip()

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