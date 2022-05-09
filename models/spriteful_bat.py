import os

import pygame

from models.helpers import image_generator
from models.spritesheet import SpriteSheet


class Bat(pygame.sprite.Sprite):
    def __init__(self, direction, step, sprite_path, *groups):
        super().__init__(*groups)
        self.dying = False
        self.dead = False
        self.death_stage = 0
        self.death_stages = 16

        self.step = step
        self.direction = direction
        fly_sprite = SpriteSheet(os.path.join(sprite_path, 'noBKG_BatAttack_strip.png'))
        death_sprite = SpriteSheet(os.path.join(sprite_path, 'noBKG_BatDeath_strip.png'))
        rects = []
        for i in range(8):
            rects.append(pygame.Rect(i * 64, 0, 64, 64))
        fly_images = fly_sprite.images_at(rects, (0, 0, 0, 255))
        death_images = death_sprite.images_at(rects, (0, 0, 0, 255))
        fly_images = [pygame.transform.scale(img, (int(img.get_width() * 1.5), int(img.get_height() * 1.5))) for img in
                      fly_images]
        death_images = [pygame.transform.scale(img, (int(img.get_width() * 1.5), int(img.get_height() * 1.5))) for img
                        in death_images]
        if self.direction < 0:
            fly_images = [pygame.transform.flip(img, True, False) for img in fly_images]
            death_images = [pygame.transform.flip(img, True, False) for img in death_images]

        self.fly_images_generator = image_generator(fly_images, 1)
        self.death_images_generator = image_generator(death_images, 2)
        self.image = next(self.fly_images_generator)
        self.rect = self.image.get_rect()
        if self.direction > 0:
            self.rect.x = 10
        else:
            self.rect.x = 835
        self.rect.y = 650
        self.collider_rect = self.rect.inflate(-80, -80)

    def update(self):
        if not self.dying:
            self.image = next(self.fly_images_generator)
            self.rect.x += self.direction * self.step
            self.collider_rect.x += self.direction * self.step
        else:
            self.collider_rect = None
            if self.death_stage < self.death_stages:
                self.image = next(self.death_images_generator)
                self.rect.y += 1
            else:
                self.dead = True
            self.death_stage += 1

    def die(self):
        self.dying = True