import os

GRID_OFFSET_X = 375
GRID_OFFSET_Y = 130
PY_TILE_W = 115
PY_TILE_H = 141

C_TILE_W = 110.0
C_TILE_H = 141.0

UI_HEIGHT = 120
CARD_W = 70
CARD_H = 90
CARD_ICON_W = 52
CARD_ICON_H = 53
CARD_ICON_OFF_X = 8
CARD_ICON_OFF_Y = 13
CARD_COST_OFF_X = 17
CARD_COST_OFF_Y = 65

SAVE_FILE = "save.json"
DLL_NAME = "TowerEngine.dll"
FONT_NAME = "font_custom.ttf"
GAME_TITLE = "Plants vs Zombies: My Version"

TEXT_GREEN = (50, 205, 50)
TEXT_WHITE = (255, 255, 255)
TEXT_BLACK = (0, 0, 0)
COLOR_HEADER = (0, 200, 0)
COLOR_BTN_TEXT = (30, 30, 30)

PLANT_COLS = [
    (0, 255, 0),
    (255, 255, 0),
    (160, 82, 45), 
    (200, 150, 50),
    (200, 0, 0), 
    (100, 200, 255)
]

PLANT_NAMES = ["Pea", "Sun", "Nut", "Mine", "Bomb", "Ice"]
PLANT_COSTS = [100, 50, 50, 25, 150, 0]

UNLOCK_INFO = {
    1: ("Sunflower", "Produces sun for economy. I couldn't animate its sun producing haha."),
    2: ("Wall-Nut", "Blocks zombies with high health. I wish I was like him."),
    3: ("Potato Mine", "Explodes when zombies step on it. Same issue as with Sunflower :("),
    4: ("Shovel", "Allows digging up plants."),
    5: ("Cherry Bomb", "Explodes immediately in an area. Its explosion animation is my most precious creation in my whole life HAHAHAHA."),
    6: ("Ice Shroom", "Freezes a zombie on contact. ")
}
