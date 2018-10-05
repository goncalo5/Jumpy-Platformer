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
HIGHSCORE_FILE = 'highscore.txt'
SPRITESHEET_DIR = ['JumperPack_Kenney', 'Spritesheets']
SPRITESHEET_FILE = 'spritesheet_jumper.png'

# Background:
BG_COLOR = LIGHTBLUE
CLOUD_DIR = ['JumperPack_Kenney', 'PNG', 'clouds']
CLOUD_LAYER = 0
CLOUD_PROB = 0.15


# Player:
PLAYER_SIZE_RATE = 0.4
PLAYER_ACC = .5
PLAYER_FRICTION = -0.12
PLAYER_G = 0.8
PLAYER_JUMP = 25
PLAYER_LAYER = 2

# Plataforms:
PLATFORM_LIST = [
    (0, HEIGHT - 60),
    (WIDTH / 2 - 50, HEIGHT * 3 / 4),
    (125, HEIGHT - 350),
    (350, 200),
    (175, 100)
]
PLATFORM_MIN = 6
PLATFORM_LAYER = 1

# powerups:
BOOST_POWER = 60
POW_SPAWN_PCT = 10
POW_LAYER = 1

# Mobs:
MOB_FREQ = 5000
MOB_LAYER = 2

# Sounds:
SOUND_DIR = 'snd'
MUSIC_GAME = 'happytune.ogg'
MUSIC_MENU = 'Yippee.ogg'
SOUND_JUMP = 'Jump.wav'
SOUND_BOOST = 'boost.wav'
