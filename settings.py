#!/usr/bin/env python
# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 200)

# game options/settings
TITLE = 'Jumpy!'
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'arial'
BG_COLOR = LIGHTBLUE
HIGHSCORE_FILE = 'highscore.txt'

# Player:
PLAYER_ACC = .5
PLAYER_FRICTION = -0.12
PLAYER_G = 0.8
PLAYER_JUMP = 20

# Plataforms:
PLATFORM_LIST = [
    (0, HEIGHT - 40, WIDTH, 40),
    (WIDTH / 2 - 50, HEIGHT * 3 / 4, 100, 20),
    (125, HEIGHT - 350, 100, 20),
    (350, 200, 100, 20),
    (175, 100, 50, 20)
]
PLATFORM_MIN = 6
