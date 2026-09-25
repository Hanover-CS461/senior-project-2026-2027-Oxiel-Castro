FONT = "game/assets/Fonts/PixelPurl.ttf"
WINDOW_SIZE = (800, 600)
ENEMY_DELAY = 1400
READ_DELAY = 600
MESSAGE_PAGE_LINES = 5
MESSAGE_MAX_WIDTH = 720

LUNA_X = 60
LUNA_ATTACK_X = 470
WALK_TIME = 400

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