#!/usr/bin/env python
from os import path
import pygame as pg
import random
from settings import *
from sprites import Player
from sprites import Platform


class Game(object):
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

        # variables:
        self.playing = None

    def load_data(self):
        # load high Score
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, HIGHSCORE_FILE), 'w') as file:
            try:
                self.highscore = int(file.read())
                print self.highscore
            except IOError:
                self.highscore = 0

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)

        for platform_settings in PLATFORM_LIST:
            platform = Platform(*platform_settings)
            self.all_sprites.add(platform)
            self.platforms.add(platform)

        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def handle_common_events(self, event):
        try:
            self.cmd_key_down
        except AttributeError:
            self.cmd_key_down = False
        # check for closing window
        if event.type == pg.QUIT:
            self.quit()

        if event.type == pg.KEYDOWN:
            if event.key == 310:
                self.cmd_key_down = True
            if self.cmd_key_down and event.key == pg.K_q:
                self.quit()

        if event.type == pg.KEYUP:
            if event.key == 310:
                self.cmd_key_down = False

    def events(self):

        # Game Loop - events
        for event in pg.event.get():
            # Game events:
            self.handle_common_events(event)

            # Other events:
            self.player.events(event)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        # check if player hits platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                self.player.pos.y = hits[0].rect.top + 1
                self.player.vel.y = 0
                # self.player.acc.y = 0
        if self.player.rect.top <= HEIGHT / 4:
            scroll = abs(self.player.vel.y)
            self.player.pos.y += scroll
            for platform in self.platforms:
                platform.rect.y += scroll
                if platform.rect.top >= HEIGHT:
                    platform.kill()
                    self.score += 10

        # spawn new platforms to keep same average number:
        while len(self.platforms) < PLATFORM_MIN:
            width = random.randrange(50, 100)
            height = 20
            x = random.randrange(0, WIDTH - width)
            y = random.randrange(-75, -35)
            p = Platform(x, y, width, height)
            self.platforms.add(p)
            self.all_sprites.add(p)

    def draw(self):
        # Game Loop - draw
        self.screen.fill(LIGHTBLUE)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        self.screen.fill(BG_COLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text('Arrows to move, Space to Jump',
                       22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text('Press a key to play',
                       22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text('High Score: %s' % self.highscore,
                       22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        self.screen.fill(BG_COLOR)
        self.draw_text('Game Over', 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text('Score: %s' % self.score,
                       22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text('Press a key to play again',
                       22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text('NEW HIGH SCORE!',
                           22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HIGHSCORE_FILE), 'w') as file:
                file.write(str(self.score))
        else:
            self.draw_text('High Score: %s' % self.highscore,
                           22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        self.waiting = True
        while self.waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.KEYUP:
                    self.waiting = False
                self.handle_common_events(event)

    def quit(self):
        self.waiting = False
        self.playing = False
        self.running = False
        # quit()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
