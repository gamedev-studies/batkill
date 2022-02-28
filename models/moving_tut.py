import pygame
import sys
import os
import random

from models.helpers import generator_from_formatter, image_generator
from models.backend_player import StandardPlayer, MOVE_LEFT, MOVE_RIGHT, JUMP, ATTACK
from models.spritesheet import SpriteSheet

'''
Objects
'''

adventurer = os.path.join('static', 'sprites', 'adventurer')
bat_sprite_path = os.path.join('static', 'sprites', 'Bat')
background = os.path.join('static', 'backgrounds', 'forest', 'background.png')


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

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        run_formatter = os.path.join(adventurer, 'adventurer-run-0{}.png')
        self.right_run_images = generator_from_formatter(run_formatter, 6)
        self.left_run_images = generator_from_formatter(run_formatter, 6, flip=True)
        idle_formatter = os.path.join(adventurer, 'adventurer-idle-2-0{}.png')
        self.idle_right = generator_from_formatter(idle_formatter, 4, flip=False, repeats=5)
        self.idle_left = generator_from_formatter(idle_formatter, 4, flip=True, repeats=5)
        attack_formatter = os.path.join(adventurer, 'adventurer-attack3-0{}.png')
        self.attack_right = generator_from_formatter(attack_formatter, 6, flip=False, repeats=1)
        self.attack_left = generator_from_formatter(attack_formatter, 6, flip=True, repeats=1)

        jumping_formatter = os.path.join(adventurer, 'adventurer-jump-0{}.png')
        self.jump_right = generator_from_formatter(jumping_formatter, 4, flip=False, repeats=2)
        self.jump_left = generator_from_formatter(jumping_formatter, 4, flip=True, repeats=2)

        falling_formatter = os.path.join(adventurer, 'adventurer-fall-0{}.png')
        self.fall_right = generator_from_formatter(falling_formatter, 2, flip=False, repeats=1)
        self.fall_left = generator_from_formatter(falling_formatter, 2, flip=True, repeats=1)

        self.image = next(self.idle_right)
        rect = self.image.get_rect()
        self.sp = StandardPlayer(x=300, y=653, ground_y=653, rect=rect, x_step=12)

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

        self.sp.rect.x = self.sp.x
        self.sp.rect.y = self.sp.y

        if not self.sp.attack.attack_poly:
            if self.sp.dy != 0:
                if self.sp.dy < 0 and self.sp.y - self.sp.ground_y < 8:
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


class Bat(pygame.sprite.Sprite):
    def __init__(self, direction, step, *groups):
        super().__init__(*groups)
        self.dying = False
        self.dead = False
        self.death_stage = 0
        self.death_stages = 16

        self.step = step
        self.direction = direction
        fly_sprite = SpriteSheet(os.path.join(bat_sprite_path, 'noBKG_BatAttack_strip.png'))
        death_sprite = SpriteSheet(os.path.join(bat_sprite_path, 'noBKG_BatDeath_strip.png'))
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


def maybe_create_bat(current_score, base_prob=50, base_speed=6):
    current_score = 0 if current_score < 0 else current_score
    current_odds = base_prob - current_score/15
    speed = int(base_speed * (1 + current_score / 20))
    if (random.random() * current_odds) + 1 > current_odds:
        print(f"New bat speed {speed}")
        return Bat(direction=random.choice([-1, 1]), step=speed)
    else:
        return None


'''
Setup
'''


worldx = 928
worldy = 793

lives = 5
score = 0

fps = 30  # frame rate
ani = 6  # animation cycles
clock = pygame.time.Clock()
pygame.init()
main = True


world = pygame.display.set_mode([worldx, worldy])
backdrop = pygame.image.load(background).convert()
backdropbox = world.get_rect()
player = Player()  # spawn player
player_list = pygame.sprite.Group()
player_list.add(player)
steps = 5  # how fast to move
pygame.font.init()
score_font = pygame.font.SysFont(os.path.join('static', 'fonts', 'SourceCodePro-Medium.ttf'), 30)
score_surface = score_font.render()

'''
Main loop
'''
loop = 0
enemies = pygame.sprite.Group()

while main == True:
    loop += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            main = False

    player_actions = []
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_actions.append(MOVE_LEFT)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_actions.append(MOVE_RIGHT)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_actions.append(JUMP)
    if keys[pygame.K_SPACE]:
        player_actions.append(ATTACK)

    player.control(player_actions)
    world.blit(backdrop, backdropbox)

    score_surface = score_font.render()
    world.blit(score_surface, (10, 10))
    new_bat = maybe_create_bat(score)
    if new_bat:
        bat = new_bat

        player_list.add(bat)
        enemies.add(bat)
    for bat in enemies:
        # if bat.collider_rect:
        #     pygame.draw.rect(world, (128, 0, 0, 200), bat.collider_rect)
        bat.update()
        if player.sp.attack.attack_poly is not None and not bat.dying:
            killed = player.sp.attack.attack_poly.rect.colliderect(bat.collider_rect)
            if killed:
                bat.die()
                score += 1
        if bat.dead:
            enemies.remove(bat)
            bat.kill()
            del bat
        elif bat.collider_rect is not None and player.sp.collider_rect.colliderect(bat.collider_rect):
            bat.die()
            lives -= 1
            score -= 5
            print('Dead')

    player_list.draw(world)
    player.update()
    player_list.draw(world)

    pygame.display.flip()
    clock.tick(fps)
