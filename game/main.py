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
    LUNA_FRAMES,
    MESSAGE_MAX_WIDTH,
    MESSAGE_PAGE_LINES,
    READ_DELAY,
    WINDOW_SIZE,
)
from sprites import load_frames
from ui import Button, draw_bar, draw_disabled_button


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

        self.luna_frames = load_frames(
            "game/assets/Luna.png", LUNA_FRAMES, size=(132, 96)
        )
        self.fly_frames = load_frames("game/assets/fly.png", FLY_FRAMES, scale=5)
        self.luna_attack_frames = load_frames(
            "game/assets/Luna.png", ATTACK_FRAMES, scale=5
        )

        self.anim_index = 0
        self.anim_timer = 0
        self.fly_index = 0
        self.fly_timer = 0
        self.attack_anim = False
        self.attack_index = 0
        self.attack_timer = 0

        self.buttons = [
            Button(300, 250, 200, 60, "Start", "start"),
            Button(300, 330, 200, 60, "Quit", "quit"),
        ]
        self.battle_buttons = [
            Button(50, 500, 180, 60, "Attack", "attack"),
            Button(250, 500, 180, 60, "Rest", "rest"),
        ]
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
        if self.attack_anim:
            if now - self.attack_timer > 80:
                self.attack_timer = now
                self.attack_index += 1
                if self.attack_index >= len(self.luna_attack_frames):
                    self.attack_anim = False
                    self.attack_index = 0
        elif now - self.anim_timer > 150:
            self.anim_timer = now
            self.anim_index = (self.anim_index + 1) % len(self.luna_frames)
        if now - self.fly_timer > 70:
            self.fly_timer = now
            self.fly_index = (self.fly_index + 1) % len(self.fly_frames)

    def draw_battle(self):
        """Draw the battle screen: sprites, bars, message, and buttons."""
        self.screen.fill(COLOR_BATTLE_BG)
        self._update_animations(pygame.time.get_ticks())
        if self.attack_anim:
            luna = self.luna_attack_frames[self.attack_index]
        else:
            luna = self.luna_frames[self.anim_index]
        self.screen.blit(luna, (60, 300))
        fly = self.fly_frames[self.fly_index]
        self.screen.blit(fly, (620 - fly.get_width() // 2, 320 - fly.get_height() // 2))

        draw_bar(
            self.screen, self.small_font, 40, 60, 300, 20,
            self.battle.player_hp, self.battle.player_hp_max, COLOR_HP_BAR,
            f"Luna HP {self.battle.player_hp}/{self.battle.player_hp_max}",
        )
        draw_bar(
            self.screen, self.small_font, 460, 60, 300, 20,
            self.battle.enemy.hp, self.battle.enemy.max_hp, COLOR_HP_BAR,
            f"Fly HP {self.battle.enemy.hp}/{self.battle.enemy.max_hp}",
        )
        draw_bar(
            self.screen, self.small_font, 40, 110, 300, 20,
            self.battle.focus, Battle.MAX_FOCUS, COLOR_FOCUS_BAR,
            f"Focus {self.battle.focus}/{Battle.MAX_FOCUS}",
        )

        lines = (
            self._message_pages[self._message_page]
            if self._message_pages
            else [self.battle.message]
        )
        y = 150
        for line in lines:
            msg = self.small_font.render(line, True, (255, 255, 255))
            self.screen.blit(msg, (40, y))
            y += 40
        if len(self._message_pages) > self._message_page + 1:
            more = self.small_font.render("...", True, COLOR_WHITE)
            self.screen.blit(more, (40, y))

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
                        self._message_pages = []
                        self._message_page = 0
                        self._message_timer = 0
                        self._last_message = None
                        self.state = "battle"
                    elif button.action == "quit":
                        self.running = False
        elif self.state == "battle":
            if self.battle.phase == "player" and not self.enemy_phase:
                for button in self.battle_buttons:
                    if button.rect.collidepoint(pos):
                        if button.action == "attack":
                            self.battle.attack()
                            if self.battle.luna_attacked:
                                self.attack_anim = True
                                self.attack_index = 0
                                self.attack_timer = pygame.time.get_ticks()
                                self.battle.luna_attacked = False
                        elif button.action == "rest":
                            self.battle.rest()
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
                    self.attack_anim = True
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