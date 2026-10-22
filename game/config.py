FONT = "game/assets/Fonts/PixelPurl.ttf"
WINDOW_SIZE = (800, 600)
ENEMY_DELAY = 1400
READ_DELAY = 1200
MESSAGE_PAGE_LINES = 5
MESSAGE_MAX_WIDTH = 720

LUNA_X = 60
LUNA_ATTACK_X = 470
ENEMY_X = 620
ENEMY_ATTACK_X = 260
WALK_TIME = 400
MAP_WALK_TIME = 1400
MAP_BATTLE_DELAY = 400
FOUND_NOTICE_TIME = 5000
FADE_TIME = 400
SPIRAL_TIME = 1200
WIPE_TIME = 1200

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BUTTON = (30, 144, 255)
COLOR_BUTTON_HOVER = (65, 105, 225)
COLOR_DISABLED = (120, 120, 120)
COLOR_DISABLED_TEXT = (180, 180, 180)
COLOR_TITLE = (174, 27, 51)
COLOR_FOUND = (60, 200, 60)
COLOR_HP_BAR = (200, 40, 40)
COLOR_FOCUS_BAR = (40, 120, 255)
COLOR_BATTLE_BG = (120, 200, 120)
COLOR_END_BG = (20, 20, 20)
COLOR_HINT = (200, 200, 200)
COLOR_HEAVY = (255, 200, 0)

# Image asset paths, grouped so every path lives in one place.
BACKGROUND_IMAGE = "game/assets/images/background.png"
CAMPUS_IMAGE = "game/assets/images/campus.png"
LUNA_SHEET = "game/assets/images/Luna2.png"
VICTORY_IMAGE = "game/assets/images/w_end.2.png"
BATTLE_BG = "game/assets/images/battle_bg.png"

# Music track paths, grouped so every track lives in one place.
MUSIC_TITLE = "game/assets/music/POL-chubby-cat.wav"
MUSIC_CAMPUS = "game/assets/music/campus_m.mp3"
MUSIC_BATTLE = "game/assets/music/battle_m.mp3"
MUSIC_BOSS = "game/assets/music/guardian_battle_m.WAV"
MUSIC_BATTLE_START = "game/assets/music/start_battle_m.mp3"
MUSIC_VICTORY = "game/assets/music/Victory.mp3"
MUSIC_DEFEAT = "game/assets/music/game_over.mp3"

# Player balance, shared by the battle and run logic.
PLAYER_MAX_HP = 100
PLAYER_START_HP = 100
PLAYER_MAX_FOCUS = 30
PLAYER_START_FOCUS = 16
PLAYER_START_AGILITY = 3
START_INVENTORY = {"wet_food": 3, "catnip": 2, "milk": 1}

# Extra damage each enemy attack gains per difficulty tier above the first.
# Easy (tier 1) keeps the base move values; Medium/Hard add this per tier.
DAMAGE_PER_TIER = 2

# Per-building battle backgrounds, keyed by building name. "guard" is the
# first fight, "boss" the second. Any building not listed uses BATTLE_BG.
BATTLE_BACKGROUNDS = {
    "Lynn Hall": {
        "guard": "game/assets/images/soda_machine.png",
        "boss": "game/assets/images/skiadas_class.png",
    },
}

# Each frame is a crop on the sheet: (x, y, width, height) in pixels.
LUNA_FRAMES = [
    (2, 7, 29, 22),
    (33, 9, 32, 20),
    (67, 11, 31, 18),
    (101, 12, 30, 19),
]

WALK_FRAMES = [
    (3, 264, 27, 18),
    (35, 264, 28, 18),
    (69, 264, 27, 18),
    (104, 264, 25, 18),
    (135, 264, 27, 18),
    (167, 264, 28, 18),
    (201, 264, 27, 18),
    (236, 264, 25, 18),
]

FLY_FRAMES = [
    (7, 105, 17, 13),
    (39, 107, 17, 14),
    (71, 109, 17, 13),
    (105, 114, 15, 13),
    (137, 117, 16, 11),
    (168, 121, 17, 7),
    (200, 122, 17, 6),
]

SNAKE_FRAMES = [
    (0, 11, 31, 21),
    (32, 11, 32, 21),
    (64, 11, 32, 21),
    (96, 11, 31, 21),
    (128, 11, 31, 21),
    (160, 12, 31, 20),
    (192, 12, 31, 20),
]

SPIDER2_FRAMES = [
    (10, 24, 11, 8),
    (42, 25, 12, 7),
    (74, 25, 12, 7),
    (106, 24, 11, 8),
    (138, 23, 11, 9),
]

RAT_FRAMES = [
    (9, 23, 14, 9),
    (41, 23, 13, 9),
    (73, 23, 15, 9),
    (105, 23, 16, 9),
    (137, 24, 14, 8),
    (169, 24, 14, 8),
    (201, 24, 13, 8),
    (233, 24, 13, 8),
    (265, 24, 14, 8),
    (297, 24, 14, 8),
]

BAT_FRAMES = [
    (7, 173, 18, 8),
    (40, 172, 16, 10),
    (74, 172, 12, 11),
    (105, 173, 14, 11),
    (135, 175, 18, 9),
    (166, 175, 20, 8),
    (198, 175, 21, 7),
    (232, 174, 17, 7),
    (264, 173, 17, 7),
    (295, 173, 19, 8),
]

ENEMY_SPRITES = {
    "fly": {"path": "game/assets/images/enemies/fly.png", "scale": 5, "frames": FLY_FRAMES},
    "snake": {"path": "game/assets/images/enemies/snake.png", "scale": 4, "frames": SNAKE_FRAMES},
    "spider_2": {"path": "game/assets/images/enemies/spider_2.png", "scale": 8, "frames": SPIDER2_FRAMES},
    "rat": {"path": "game/assets/images/enemies/rat_and_bat.png", "scale": 12, "frames": RAT_FRAMES},
    "bat": {"path": "game/assets/images/enemies/rat_and_bat.png", "scale": 6, "frames": BAT_FRAMES},
}

ATTACK_FRAMES = [
    (5, 456, 25, 17),
    (39, 455, 22, 18),
    (73, 453, 20, 20),
    (107, 452, 22, 21),
    (140, 452, 21, 21),
    (173, 452, 21, 21),
    (206, 452, 21, 21),
    (239, 452, 18, 21),
    (272, 452, 18, 21),
    (305, 452, 22, 21),
    (337, 453, 20, 20),
    (369, 455, 22, 18),
    (401, 456, 25, 17),
]

# Defeat screen: Luna curled in her box with a paw poking out (crop on Luna2.png).
DEFEAT_FRAME = (69, 556, 29, 15)
DEFEAT_SCALE = 12