"""Background music playback and track hand-off.

Wraps pygame.mixer so the rest of the game can ask for a theme by name
without juggling load/play/queue calls. The battle-start sting hands off
to the looping battle theme via an end-of-track event.
"""

import pygame

from config import (
    MUSIC_BATTLE,
    MUSIC_BATTLE_START,
    MUSIC_BOSS,
    MUSIC_CAMPUS,
    MUSIC_DEFEAT,
    MUSIC_TITLE,
    MUSIC_VICTORY,
)

BATTLE_MUSIC_EVENT = pygame.USEREVENT + 1


class Music:
    """Loads and plays the game's music tracks."""

    def __init__(self):
        """Initialise the mixer and remember the default battle loop."""
        self._pending = False
        self._loop_track = MUSIC_BATTLE
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_endevent(BATTLE_MUSIC_EVENT)
        except pygame.error:
            pass

    def _play(self, path, loops=0):
        """Stop the current track and play path, looping when loops is set."""
        self._pending = False
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops=loops)
        except pygame.error:
            pass

    def play_title(self):
        """Loop the title theme; only used on the title screen."""
        self._play(MUSIC_TITLE, loops=-1)

    def play_campus(self):
        """Loop the campus theme for the intro and map scenes."""
        self._play(MUSIC_CAMPUS, loops=-1)

    def play_victory(self):
        """Play the victory theme when the run is won."""
        self._play(MUSIC_VICTORY)

    def play_defeat(self):
        """Play the game-over theme when the run is lost."""
        self._play(MUSIC_DEFEAT)

    def play_battle(self, boss=False):
        """Play the battle-start sting, then hand off to the battle theme."""
        self._loop_track = MUSIC_BOSS if boss else MUSIC_BATTLE
        self._play(MUSIC_BATTLE_START)
        self._pending = True
        try:
            pygame.mixer.music.queue(self._loop_track)
        except pygame.error:
            pass

    def play_battle_loop(self):
        """Loop the battle theme once the battle-start sting ends."""
        self._play(self._loop_track, loops=-1)

    def handle_event(self, event):
        """Start the battle loop when the sting finishes, if one is pending."""
        if event.type == BATTLE_MUSIC_EVENT and self._pending:
            self._pending = False
            self.play_battle_loop()
