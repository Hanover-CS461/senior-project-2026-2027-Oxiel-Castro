import re

import pygame

from battle import Battle
from config import (
    ATTACK_FRAMES,
    COLOR_BATTLE_BG,
    COLOR_END_BG,
    COLOR_FOCUS_BAR,
    COLOR_HP_BAR,
    COLOR_TITLE,
    ENEMY_DELAY,
    FLY_FRAMES,
    FONT,
    LUNA_ATTACK_X,
    LUNA_FRAMES,
    LUNA_X,
    MESSAGE_MAX_WIDTH,
    MESSAGE_PAGE_LINES,
    READ_DELAY,
    WALK_FRAMES,
    WALK_TIME,
    WINDOW_SIZE,
    COLOR_WHITE,
)
from sprites import load_frames
from ui import Button, draw_bar, draw_disabled_button, draw_outlined_text


class Game:
    """Main game loop, input handling, and drawing."""

    def __init__(self):
        """Set up pygame, load assets, and create the UI buttons."""
        pygame.init()
        pygame.mixer.init()

        pygame.mixer.music.load("game/assets/music/POL-chubby-cat.wav")
        pygame.mixer.music.play(loops=-1)
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Luna - a Hanover College Mystery")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT, 50)
        self.small_font = pygame.font.Font(FONT, 32)
        self.title_font = pygame.font.Font(FONT, 60)
        self.state = "menu"

        self.background = pygame.image.load("game/assets/background.png").convert()
        self.background = pygame.transform.scale(self.background, WINDOW_SIZE)
        self.battle_bg = pygame.image.load("game/assets/battle_bg.png").convert()
        self.battle_bg = pygame.transform.scale(self.battle_bg, WINDOW_SIZE)

        self.luna_frames = load_frames(
            "game/assets/Luna2.png", LUNA_FRAMES, size=(132, 96)
        )
        self.walk_frames = load_frames(
            "game/assets/Luna2.png", WALK_FRAMES, scale=5
        )
        self.fly_frames = load_frames("game/assets/fly.png", FLY_FRAMES, scale=5, flip=True)
        self.luna_attack_frames = load_frames(
            "game/assets/Luna2.png", ATTACK_FRAMES, scale=5
        )

        self.anim_index = 0
        self.anim_timer = 0
        self.fly_index = 0
        self.fly_timer = 0
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
            Button(20, 500, 180, 60, "Attack", "attack"),
            Button(210, 500, 180, 60, "Defend", "defend"),
            Button(400, 500, 180, 60, "Rest", "rest"),
            Button(590, 500, 180, 60, "Instincts", "instincts")
        ]
        self.instinct_spots = [
            ("night_vision", 140, 430),
            ("prowl", 380, 430),
            ("yowl", 140, 490),
            ("nine_lives", 380, 490),
        ]
        self.instinct_buttons = [
            Button(x, y, 220, 55, f"{Battle.INSTINCTS[name]['name']} ({Battle.INSTINCTS[name]['cost']})", name)
            for name, x, y in self.instinct_spots
        ]
        self.back_button = Button(620, 430, 140, 55, "Back", "back")
        self.submenu = False
        self.menu_button = Button(300, 400, 200, 60, "Menu", "menu")

        self.battle = None
        self.enemy_phase = False
        self.enemy_timer = 0
        self._message_pages = []
        self._message_page = 0
        self._message_timer = 0
        self._last_message = None

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

    def _update_animations(self, now):
        """Advance the cat and fly animation frames based on elapsed time."""
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
        if now - self.fly_timer > 70:
            self.fly_timer = now
            self.fly_index = (self.fly_index + 1) % len(self.fly_frames)

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
        fly = self.fly_frames[self.fly_index]
        self.screen.blit(fly, (620 - fly.get_width() // 2, 360 - fly.get_height() // 2))

        draw_outlined_text(
            self.screen, self.small_font,
            f"Luna HP {self.battle.player_hp}/{self.battle.player_hp_max}", (40, 30),
        )
        draw_outlined_text(
            self.screen, self.small_font,
            f"Fly HP {self.battle.enemy.hp}/{self.battle.enemy.max_hp}", (460, 30),
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

        if self.submenu:
            for button in self.instinct_buttons:
                disabled = self.enemy_phase or not self.battle.can_use_instinct(button.action)
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

    def handle_click(self, pos):
        """Route a mouse click to the current screen's buttons."""
        if self.state == "menu":
            for button in self.buttons:
                if button.rect.collidepoint(pos):
                    if button.action == "start":
                        self.battle = Battle()
                        self.enemy_phase = False
                        self.enemy_timer = 0
                        self.submenu = False
                        self._message_pages = []
                        self._message_page = 0
                        self._message_timer = 0
                        self._last_message = None
                        self.state = "battle"
                    elif button.action == "quit":
                        self.running = False
        elif self.state == "battle":
            if self.battle.phase == "player" and not self.enemy_phase:
                if self.submenu:
                    if self.back_button.rect.collidepoint(pos):
                        self.submenu = False
                    for button in self.instinct_buttons:
                        if button.rect.collidepoint(pos):
                            self.battle.use_instinct(button.action)
                            self.submenu = False
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
                            elif button.action == "instincts":
                                self.submenu = True
                if self.battle.over:
                    self.state = "victory" if self.battle.won else "defeat"
                elif self.battle.phase == "enemy":
                    self.enemy_phase = True
                    self.enemy_timer = pygame.time.get_ticks()
        elif self.state in ("victory", "defeat"):
            if self.menu_button.rect.collidepoint(pos):
                self.state = "menu"

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
                    self.state = "victory" if self.battle.won else "defeat"
        elif self._message_done() and now - self._message_timer > READ_DELAY:
            self.enemy_phase = False
        else:
            self._advance_message(now)

    def run(self):
        """Run the main loop: handle events, draw the state, flip the display."""
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "battle":
                self.draw_battle()
                self.update_battle()
            elif self.state == "victory":
                self.draw_end("You win! The fly is gone.")
            elif self.state == "defeat":
                self.draw_end("You were defeated.")
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    Game().run()