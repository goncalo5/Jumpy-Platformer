#!/usr/bin/env python
import random
import pygame as pg
from settings import *
vec = pg.math.Vector2


class Spritesheet(object):
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):

        try:
            self.spritesheet = pg.image.load(filename).convert()
        except pg.error:
            self.spritesheet = None

    def get_image(self, x, y, width, height):
        x, y, width, height = int(x), int(y), int(width), int(height)
        width_real = int(width * PLAYER_SIZE_RATE)
        height_real = int(height * PLAYER_SIZE_RATE)
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        try:
            image.blit(self.spritesheet, (0, 0), (x, y, width, height))
            image.set_colorkey(BLACK)
            image = pg.transform.scale(image, (width_real, height_real))
        except TypeError:
            image = pg.Surface((width_real, height_real))
            image.fill(YELLOW)
        return image


class Cloud(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = CLOUD_LAYER
        self.groups = game.all_sprites, game.clouds
        super(Cloud, self).__init__(self.groups)
        self.game = game
        self.image = random.choice(self.game.cloud_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        scale = random.randrange(50, 100) / 100.
        self.image = pg.transform.scale(self.image,
                                        (int(self.rect.width * scale),
                                         int(self.rect.height * scale)))
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-500, -50)
        self.scroll_rate = random.random()

    def update(self):
        if self.rect.top > HEIGHT * 2:
            self.kill()


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        super(Player, self).__init__(self.groups)
        self.game = game

        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]

        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT - 100)
        self.pos = self.rect.center
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [
            self.game.spritesheet.get_image(
                x="614", y="1063", width="120", height="191"),
            self.game.spritesheet.get_image(
                x="690", y="406", width="120", height="201")
        ]

        self.walking_frames = {}
        self.walking_frames['right'] = [
            self.game.spritesheet.get_image(
                x="678", y="860", width="120", height="201"),
            self.game.spritesheet.get_image(
                x="692", y="1458", width="120", height="207")
        ]
        self.walking_frames['left'] = []
        for frame in self.walking_frames['right']:
            frame_fliped = pg.transform.flip(frame, True, False)
            self.walking_frames['left'].append(frame_fliped)

        self.jump_frame = self.game.spritesheet.get_image(
            x="382", y="763", width="150", height="181")

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -8:
                self.vel.y = -8

    def jump(self):
        # Jump only if standing on a platform
        self.rect.x += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 2
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP
            self.game.jump_sound.play()

    def events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.jump()
        if event.type == pg.KEYUP:
            if event.key == pg.K_SPACE:
                self.jump_cut()

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_G)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # aplly the friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < .5:
            self.vel.x = 0
        self.pos += self.vel + self.acc / 2.
        # wrap around the sides of the Screen
        if self.pos.x + self.rect.width / 2. < 0:
            self.pos.x = WIDTH + self.rect.width / 2.
        if self.pos.x - self.rect.width / 2. > WIDTH:
            self.pos.x = -self.rect.width / 2.

        self.rect.midbottom = self.pos

        # Die!
        if self.rect.top > HEIGHT:
            scroll = max(self.vel.y, 10)
            for sprite in self.game.all_sprites:
                sprite.rect.y -= scroll
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.game.platforms) == 0:
            self.game.playing = False

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        # show the walk animation
        if self.walking:
            if now - self.last_update > 200:
                self.last_update = now
                direction = 'right' if self.vel.x > 0 else 'left'
                self.current_frame = (self.current_frame + 1) %\
                    len(self.walking_frames[direction])
                bottom = self.rect.bottom
                self.image = self.walking_frames[direction][self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # show the idle animation
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        self.mask = pg.mask.from_surface(self.image)


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        super(Platform, self).__init__(self.groups)
        self.game = game
        images = [
            self.game.spritesheet.get_image(
                x="0", y="288", width="380", height="94"),
            self.game.spritesheet.get_image(
                x="213", y="1662", width="201", height="100")
        ]
        self.image = random.choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if random.randrange(100) < POW_SPAWN_PCT:
            Pow(self.game, self)


class Pow(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        super(Pow, self).__init__(self.groups)
        self.game = game
        self.plat = plat
        self.type = random.choice(['boost'])
        self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()


class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        super(Mob, self).__init__(self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice([-100, WIDTH + 100])  # left or right
        self.vx = random.randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = random.randrange(HEIGHT / 2)
        self.vy = 0
        self.ay = 0.5

    def update(self):
        self.rect.x += self.vx
        self.vy += self.ay
        if self.vy > 3 or self.vy < -3:
            self.ay *= -1
        center = self.rect.center
        if self.ay < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()
