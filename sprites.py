#!/usr/bin/env python
import pygame as pg
from settings import *
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        super(Player, self).__init__()
        self.game = game
        self.image = pg.Surface((30, 40))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = self.rect.center
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def jump(self):
        # Jump only if standing on a platform
        # self.rect.x += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        # self.rect.x -= 1
        if hits:
            self.vel.y = -PLAYER_JUMP

    def events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.jump()

    def update(self):
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
        self.pos += self.vel + self.acc / 2.
        # wrap around the sides of the Screen
        if self.pos.x + self.rect.width / 2. < 0:
            self.pos.x = WIDTH
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


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super(Platform, self).__init__()
        self.image = pg.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
