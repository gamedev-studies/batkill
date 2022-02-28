import os

import pygame

from models.helpers import generator_from_formatter
from models.backend_player import StandardPlayer


class Player(pygame.sprite.Sprite):

    @staticmethod
    def jump(height=5):
        n = 0
        while n < height:
            n += 1
            yield 1
        while n > 0:
            yield -1
        return False

    def __init__(self, sprite_dir):
        pygame.sprite.Sprite.__init__(self)

        run_formatter = os.path.join(sprite_dir, 'adventurer-run-0{}.png')
        self.right_run_images = generator_from_formatter(run_formatter, 6)
        self.left_run_images = generator_from_formatter(run_formatter, 6, flip=True)
        idle_formatter = os.path.join(sprite_dir, 'adventurer-idle-2-0{}.png')
        self.idle_right = generator_from_formatter(idle_formatter, 4, flip=False, repeats=5)
        self.idle_left = generator_from_formatter(idle_formatter, 4, flip=True, repeats=5)
        attack_formatter = os.path.join(sprite_dir, 'adventurer-attack3-0{}.png')
        self.attack_right = generator_from_formatter(attack_formatter, 6, flip=False, repeats=1)
        self.attack_left = generator_from_formatter(attack_formatter, 6, flip=True, repeats=1)

        jumping_formatter = os.path.join(sprite_dir, 'adventurer-jump-0{}.png')
        self.jump_right = generator_from_formatter(jumping_formatter, 4, flip=False, repeats=2)
        self.jump_left = generator_from_formatter(jumping_formatter, 4, flip=True, repeats=2)

        falling_formatter = os.path.join(sprite_dir, 'adventurer-fall-0{}.png')
        self.fall_right = generator_from_formatter(falling_formatter, 2, flip=False, repeats=1)
        self.fall_left = generator_from_formatter(falling_formatter, 2, flip=True, repeats=1)

        self.image = next(self.idle_right)

        collider_rect = pygame.Rect(335, 673, 30, 54)
        rect = pygame.Rect(300, 653, 100, 74)
        self.sp = StandardPlayer(ground_y=653, rect=rect, collider_rect=collider_rect, x_step=12)


    @property
    def rect(self):
        return self.sp.rect

    def control(self, actions=None):
        '''
        control player movement
        '''
        if actions is None:
            actions = []
        self.sp.update(actions)

    def update(self):
        '''
        Update sprite position
        '''

        if not self.sp.attack.attack_poly:
            if self.sp.dy != 0:
                if self.sp.dy < 0 and self.sp.rect.y - self.sp.ground_y < 8:
                    if self.sp.facing > 0:
                        self.image = next(self.jump_right)
                    else:
                        self.image = next(self.jump_left)
                else:
                    if self.sp.facing > 0:
                        self.image = next(self.fall_right)
                    else:
                        self.image = next(self.fall_left)
            elif self.sp.dx != 0:
                if self.sp.facing > 0:
                    self.image = next(self.right_run_images)
                else:
                    self.image = next(self.left_run_images)
            else:
                if self.sp.facing > 0:
                    self.image = next(self.idle_right)
                else:
                    self.image = next(self.idle_left)
        elif self.sp.attack.attack_poly:
            if self.sp.facing > 0:
                self.image = next(self.attack_right)
            else:
                self.image = next(self.attack_left)