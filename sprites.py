import pygame
from PrimarySettings import *
import random


vector = pygame.math.Vector2


import pygame
from PrimarySettings import *
import random

vector = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_image
        self.rect = self.image.get_rect()
        self.hit_rect = player_box
        self.hit_rect.center = self.rect.center
        self.vel = vector(0, 0)
        self.position = vector(x, y) * SQSIZE
        self.rot = 180  # degree
        self.last_fire = 0
        self.action = None

    def set_action(self, action):
        self.action = action

    def keys(self):
        # get key for velocity every frame
        self.rotation_speed = 0  # not rotating
        self.vel = vector(0, 0)
        if self.action is not None:
            if self.action == 'left':
                self.rotation_speed = +RotationSpeedOfPlayer
            elif self.action == 'right':
                self.rotation_speed = -RotationSpeedOfPlayer
            elif self.action == 'up':
                self.vel = vector(0, playerSpeed).rotate(-self.rot)
            elif self.action == 'down':
                self.vel = vector(0, -playerSpeed).rotate(-self.rot)
            elif self.action == 'fire':
                ''''''
                now = pygame.time.get_ticks()
                if now - self.last_fire > bullet_rate:
                    self.last_fire = now
                    direction = vector(0, 1).rotate(-self.rot)
                    position = self.position + turret.rotate(-self.rot)
                    Bullet(self.game, position, direction)
                    self.game.shoot_sound.play()
                ''''''
                    
            self.action = None

    def collide_with_walls(self, direction):
        if direction == 'x_direction':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide)
            if hits:
                if self.vel.x > 0:
                    self.position.x = hits[0].rect.left - self.hit_rect.width / 2
                if self.vel.x < 0:
                    self.position.x = hits[0].rect.right + self.hit_rect.width / 2
                self.vel.x = 0
                self.hit_rect.centerx = self.position.x
        if direction == 'y_direction':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide)
            if hits:
                if self.vel.y > 0:
                    self.position.y = hits[0].rect.top - self.hit_rect.height / 2
                if self.vel.y < 0:
                    self.position.y = hits[0].rect.bottom + self.hit_rect.height / 2
                self.vel.y = 0
                self.hit_rect.centery = self.position.y

    def update(self):
        self.keys()
        self.rot = (self.rot + self.rotation_speed * self.game.changing_time) % 360
        self.image = pygame.transform.rotate(self.game.player_image, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        self.position += self.vel * self.game.changing_time
        self.hit_rect.centerx = self.position.x
        self.collide_with_walls('x_direction')
        self.hit_rect.centery = self.position.y
        self.collide_with_walls('y_direction')
        self.rect.center = self.hit_rect.center

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.enemy_image
        self.rect = self.image.get_rect()
        self.hit_rect = enemy_box
        self.hit_rect.center = self.rect.center
        self.vel = vector(0, 0)
        self.position = vector(x, y) * SQSIZE
        self.rot = 0  # degree
        self.last_fire = 0
        self.action = None

    def set_action(self, action):
        self.action = action

    def keys(self):
        # get key for velocity every frame
        self.rotation_speed = 0  # not rotating
        self.vel = vector(0, 0)
        if self.action is not None:
            if self.action == 'left':
                self.rotation_speed = +RotationSpeedOfEnemy
            elif self.action == 'right':
                self.rotation_speed = -RotationSpeedOfEnemy
            elif self.action == 'up':
                self.vel = vector(0, enemySpeed).rotate(-self.rot)
            elif self.action == 'down':
                self.vel = vector(0, -enemySpeed / 2).rotate(-self.rot)
            elif self.action == 'fire':
                '''
                now = pygame.time.get_ticks()
                if now - self.last_fire > bullet_rate:
                    self.last_fire = now
                    direction = vector(0, 1).rotate(-self.rot)
                    position = self.position + turret.rotate(-self.rot)
                    Bullet(self.game, position, direction)
                    self.game.shoot_sound.play()
                    '''
            self.action = None

    def collide_with_walls(self, direction):
        if direction == 'x_direction':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide)
            if hits:
                if self.vel.x > 0:
                    self.position.x = hits[0].rect.left - self.hit_rect.width / 2
                if self.vel.x < 0:
                    self.position.x = hits[0].rect.right + self.hit_rect.width / 2
                self.vel.x = 0
                self.hit_rect.centerx = self.position.x
        if direction == 'y_direction':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide)
            if hits:
                if self.vel.y > 0:
                    self.position.y = hits[0].rect.top - self.hit_rect.height / 2
                if self.vel.y < 0:
                    self.position.y = hits[0].rect.bottom + self.hit_rect.height / 2
                self.vel.y = 0
                self.hit_rect.centery = self.position.y

    def update(self):
        self.keys()
        self.rot = (self.rot + self.rotation_speed * self.game.changing_time) % 360
        self.image = pygame.transform.rotate(self.game.enemy_image, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        self.position += self.vel * self.game.changing_time
        self.hit_rect.centerx = self.position.x
        self.collide_with_walls('x_direction')
        self.hit_rect.centery = self.position.y
        self.collide_with_walls('y_direction')
        self.rect.center = self.hit_rect.center

# -----------------------------------------------------------------------------------------------------------------


class Explosion(pygame.sprite.Sprite):
    def __init__(self, game, center):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.explosion_list[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.picture = 0
        self.last_time_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):  # change the image when enough time has gone
        now = pygame.time.get_ticks()
        if now - self.last_time_update > self.frame_rate:
            self.last_time_update = now
            self.picture += 1
            if self.picture == len(self.game.explosion_list):
                self.kill()
            else:  # we should go to next new image
                center = self.rect.center  # next image on center
                self.image = self.game.explosion_list[self.picture]
                self.rect = self.image.get_rect()    # get the new rect for new picture
                self.rect.center = center
# ---------------------------------------------------------------------------------------------------------------------


class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, position, direction):
        self.groups = game.all_sprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_image
        self.rect = self.image.get_rect()
        self.hit_rect = bullet_box
        self.hit_rect.center = self.rect.center
        self.position = vector(position)
        self.rect.center = position
        self.vel = direction * bulletSpeed
        self.product_bullet_time = pygame.time.get_ticks()

    def update(self):
        self.position += self.vel * self.game.changing_time
        self.rect.center = self.position  # update our rectangle to that location
        if pygame.sprite.spritecollide(self, self.game.walls, False):
            if self.vel.y > 0 and self.vel.x == 0:
                self.vel *= -1
            elif self.vel.y < 0 and self.vel.x == 0:
                self.vel *= -1
            elif self.vel.x > 0 and self.vel.y == 0:
                self.vel *= -1
            elif self.vel.x < 0 and self.vel.y == 0:
                self.vel *= -1
            elif self.vel.x > 0 and self.vel.y < 0:
                self.vel.x = -self.vel.x
            elif self.vel.x < 0 and self.vel.y < 0:
                self.vel.y = -self.vel.y
            elif self.vel.x < 0 and self.vel.y > 0:
                self.vel.x = -self.vel.x
            elif self.vel.x > 0 and self.vel.y > 0:
                self.vel.y = -self.vel.y
        if pygame.time.get_ticks() - self.product_bullet_time > Bullet_life_time:
            self.kill()
# ---------------------------------------------------------------------------------------------------------------------


class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)  # initialize it with those two group
        self.image = game.wall_image
        #self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * SQSIZE
        self.rect.y = y * SQSIZE
# ---------------------------------------------------------------------------------------------------------------------


