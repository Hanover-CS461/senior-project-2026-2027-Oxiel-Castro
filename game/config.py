FONT = "game/assets/Fonts/PixelPurl.ttf"
WINDOW_SIZE = (800, 600)
ENEMY_DELAY = 1400
READ_DELAY = 600
MESSAGE_PAGE_LINES = 5
MESSAGE_MAX_WIDTH = 720

# Difficulty label and color for each building tier.
DIFFICULTY_LABELS = {0: "Easy", 1: "Medium", 2: "Hard", 3: "Very Hard"}
DIFFICULTY_COLORS = {
    0: (120, 220, 120),
    1: (255, 220, 80),
    2: (255, 160, 60),
    3: (255, 80, 80),
}

LUNA_X = 60
LUNA_ATTACK_X = 470
WALK_TIME = 400
MAP_WALK_TIME = 1400
MAP_BATTLE_DELAY = 400

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BUTTON = (30, 144, 255)
COLOR_BUTTON_HOVER = (65, 105, 225)
COLOR_DISABLED = (120, 120, 120)
COLOR_DISABLED_TEXT = (180, 180, 180)
COLOR_TITLE = (174, 27, 51)
COLOR_HP_BAR = (200, 40, 40)
COLOR_FOCUS_BAR = (40, 120, 255)
COLOR_BATTLE_BG = (120, 200, 120)
COLOR_END_BG = (20, 20, 20)

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
    "fly": {"path": "game/assets/enemies/fly.png", "scale": 5, "frames": FLY_FRAMES},
    "snake": {"path": "game/assets/enemies/snake.png", "scale": 4, "frames": SNAKE_FRAMES},
    "spider_2": {"path": "game/assets/enemies/spider_2.png", "scale": 8, "frames": SPIDER2_FRAMES},
    "rat": {"path": "game/assets/enemies/rat_and_bat.png", "scale": 12, "frames": RAT_FRAMES},
    "bat": {"path": "game/assets/enemies/rat_and_bat.png", "scale": 6, "frames": BAT_FRAMES},
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