#!/usr/bin/env python

# Art from Kenney.nl
# Happy Tune by https://opengameart.org/users/snabisch
# Yippee by https://opengameart.org/users/syncopika

from os import path
import pygame as pg
import random
from settings import *
from sprites import Player
from sprites import Platform
from sprites import Spritesheet, Mob, Cloud


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
        self.spritesheet_dir = self.dir
        for dir in SPRITESHEET_DIR:
            self.spritesheet_dir = path.join(self.spritesheet_dir, dir)
        self.spritesheet_img =\
            path.join(self.spritesheet_dir, SPRITESHEET_FILE)

        with open(path.join(self.dir, HIGHSCORE_FILE), 'w') as file:
            try:
                self.highscore = int(file.read())
            except IOError as ex:
                print(ex)
                self.highscore = 0

        # load spritesheet image
        self.spritesheet = Spritesheet(self.spritesheet_img)

        # cloud images:
        self.cloud_dir = self.dir
        for dir in CLOUD_DIR:
            self.cloud_dir = path.join(self.cloud_dir, dir)
        self.cloud_images = []
        for i in range(1, 4):
            cloud_path = path.join(self.cloud_dir, 'cloud%s.png' % i)
            self.cloud_images.append(pg.image.load(cloud_path).convert())
        # load sounds:
        self.snd_dir = path.join(self.dir, SOUND_DIR)
        try:
            sound_jump_path = path.join(self.snd_dir, SOUND_JUMP)
            self.jump_sound = pg.mixer.Sound(sound_jump_path)
        except pg.error as ex:
            print(ex)
        try:
            sound_boost_path = path.join(self.snd_dir, SOUND_BOOST)
            self.boost_sound = pg.mixer.Sound(sound_boost_path)
        except pg.error as ex:
            print(ex)

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.player = Player(self)

        for platform_settings in PLATFORM_LIST:
            Platform(self, *platform_settings)
        for i in range(5):
            c = Cloud(self)
            c.rect.y += HEIGHT
        self.mob_timer = 0
        self.time_to_next_mob = max(2000, MOB_FREQ * random.random())
        try:
            pg.mixer.music.load(path.join(self.snd_dir, MUSIC_GAME))
        except pg.error as ex:
            print(ex)
        self.run()

    def run(self):
        # Game Loop
        try:
            pg.mixer.music.play(loops=-1)
        except pg.error as ex:
            print(ex)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        try:
            pg.mixer.music.fadeout(500)
        except pygame.error as ex:
            print(ex)

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

        # spwan a mob ?
        now = pg.time.get_ticks()
        if now - self.mob_timer > self.time_to_next_mob:
            self.mob_timer = now
            self.time_to_next_mob = max(2000, MOB_FREQ * random.random())
            Mob(self)
        # hit mobs ?
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False,
                                           pg.sprite.collide_mask)
        if mob_hits:
            self.playing = False
        # check if player hits platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if lowest.rect.left < self.player.pos.x < lowest.rect.right:
                    if self.player.rect.bottom < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top + 1
                        self.player.vel.y = 0
                        self.player.jumping = False
                # self.player.acc.y = 0
        # if player reaches top 1/4 of screen:
        if self.player.rect.top <= HEIGHT / 4:
            scroll = max(abs(self.player.vel.y), 2)
            if random.random() < CLOUD_PROB:
                Cloud(self)
            for cloud in self.clouds:
                cloud.rect.y += scroll * cloud.scroll_rate
            self.player.pos.y += scroll
            for mob in self.mobs:
                mob.rect.y += scroll
            for platform in self.platforms:
                platform.rect.y += scroll
                if platform.rect.top >= HEIGHT:
                    platform.kill()
                    self.score += 10

        # if player hits powerup
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False

        # spawn new platforms to keep same average number:
        while len(self.platforms) < PLATFORM_MIN:
            width = random.randrange(50, 100)
            height = 20
            x = random.randrange(0, WIDTH - width)
            y = random.randrange(-75, -35)
            Platform(self, x, y)
            # p = Platform(self, x, y)
            # self.platforms.add(p)
            # self.all_sprites.add(p)

    def draw(self):
        # Game Loop - draw
        self.screen.fill(LIGHTBLUE)
        self.all_sprites.draw(self.screen)
        # self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        try:
            pg.mixer.music.load(path.join(self.snd_dir, MUSIC_MENU))
            pg.mixer.music.play(loops=-1)
        except pg.error as ex:
            print(ex)
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
        pg.mixer.music.fadeout(500)

    def show_go_screen(self):
        # game over/continue
        try:
            pg.mixer.music.load(path.join(self.snd_dir, MUSIC_MENU))
            pg.mixer.music.play(loops=-1)
        except pg.error as ex:
            print(ex)
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
        try:
            pg.mixer.music.fadeout(500)
        except pg.game as ex:
            print(ex)

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
