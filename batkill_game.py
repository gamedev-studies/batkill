import logging
import math
import os
import string
import sys
from traceback import print_tb
import numpy as np
import random

import pygame
from models.enemy_generation import random_bat

from models.spriteful_player import Player
from models.backend_player import MOVE_LEFT, MOVE_RIGHT, JUMP, ATTACK

class Event():
    def __init__(self, score, lives, player, worldx, worldy, sorted_bats, max_bats, pixl_arr, moving_towards, facing_nearest_bat):
        self.score = score
        self.lives = lives
        self.player = player
        self.worldx = worldx
        self.worldy = worldy
        self.sorted_bats = sorted_bats
        self.max_bats = max_bats
        self.pixl_arr = pixl_arr
        self.moving_towards = moving_towards
        self.facing_nearest_bat = facing_nearest_bat
        pass

class Observer():
    def __init__(self):
        self.event = None

    def update(self, event: Event):
        self.event = event

class Command():
    def __init__(self, key_pressed: int):
        self.key_pressed = key_pressed 

    def keyPressed(self) -> string:
        return self.key_pressed

###

bat_sprite_path = os.path.join('static', 'sprites', 'Bat')
background = os.path.join('static', 'backgrounds', 'forest', 'background.png')
adventurer_sprites = os.path.join('static', 'sprites', 'adventurer')

class Batkill():
    worldx = 928
    worldy = 793

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self,observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, event: Event) -> None:
        for observer in self._observers:
            observer.update(event)

    def __init__(self, max_bats=2, bat_speed=6, attack_cooldown=10, jump=False) -> None:
        self._observers = []
        self.max_bats = max_bats
        self.bat_speed = bat_speed
        self.attack_cooldown = attack_cooldown
        self.jump = jump
        self.initializeValues()
    
    def initializeValues(self) -> None:

        logging.basicConfig(format='%(asctime)s.%(msecs)03d %(message)s',
                            datefmt='%H:%M:%S',
                            filename='commands.log',
                            filemode='w',
                            encoding='utf-8',
                            level=logging.INFO)

        pygame.init()
        pygame.font.init()
        
        self.deterministic_bats = False
        self.sorted_bats = {n: None for n in range(self.max_bats)}

        self.loop = 0

        self.lives = 5
        self.score = 0

        self.fps = 30  # frame rate
        self.clock = pygame.time.Clock()

        self.world = pygame.display.set_mode([self.worldx, self.worldy])
        self.backdrop = pygame.image.load(background).convert()
        self.backdropbox = self.world.get_rect()
        self.player = Player(adventurer_sprites, self.attack_cooldown)  # spawn player        
        self.player_list = pygame.sprite.Group()
        self.player_list.add(self.player)

        self.score_font = pygame.font.SysFont(os.path.join('static', 'fonts', 'SourceCodePro-Medium.ttf'), 30)
        self.score_surface = self.score_font.render(f"SCORE: {round(self.score * 1000)}, LIVES: {self.lives}", True,
                                                      (0, 0, 0, 0))

        self.enemies = pygame.sprite.Group()
        self.running = True

        self.dt = 1

        event = Event(self.score, self.lives, self.player, self.worldx, self.worldy, self.sorted_bats, self.max_bats, np.array([]), False, False)
        self.notify(event)

    def gameInput(self):
        player_actions = []
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_actions.append(MOVE_LEFT)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_actions.append(MOVE_RIGHT)
        if self.jump:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player_actions.append(JUMP)
        if keys[pygame.K_SPACE]:
            player_actions.append(ATTACK)
        return player_actions

    def gameUpdate(self, command: Command) -> bool:
        moving_towards = False

        attained_score = 0

        action = command.keyPressed()

        if action is None:
            action = []
        self.actions = action

        logging.info(str(action) +
                     " -time " + str(self.clock.get_time()) +
                     " -raw-time " + str(self.clock.get_rawtime()) +
                     " -fps " + str(math.ceil(self.clock.get_fps()))) 

        self.player.control(action, self.dt)

        if any([v is None for v in self.sorted_bats.values()]):
            new_bat = random_bat(current_score=self.score, sprite_path=bat_sprite_path, base_speed=self.bat_speed)
            if new_bat:
                for k, v in self.sorted_bats.items():
                    if v is None:
                        self.sorted_bats[k] = new_bat
                        self.player_list.add(new_bat)
                        self.enemies.add(new_bat)
                        break

        for idx, bat in self.sorted_bats.items():
            if bat is not None:
                bat.update()
                if bat.direction == -1:
                    if bat.rect.x < self.player.sp.rect.x:
                        moving_towards = True
                else:
                    if bat.rect.x > self.player.sp.rect.x:
                        moving_towards = True

                if self.player.sp.attack.attack_poly is not None and not bat.dying:
                    killed = self.player.sp.attack.attack_poly.rect.colliderect(bat.collider_rect)
                    if killed:
                        bat.die()
                        attained_score += 1                        
                if bat.dead or bat.rect.x > self.worldx or bat.rect.x < 0:
                    self.enemies.remove(bat)
                    bat.kill()
                    self.sorted_bats[idx] = None
                    del bat
                elif bat.collider_rect is not None and self.player.sp.collider_rect.colliderect(bat.collider_rect):
                    bat.die()
                    self.lives -= 1

        facing_nearest_bat = self._check_facing_nearest_bat()

        self.score += attained_score

        event = Event(self.score, self.lives, self.player, self.worldx, self.worldy, self.sorted_bats, self.max_bats, self.world, moving_towards, facing_nearest_bat)
        self.notify(event)

        return True

    def _check_facing_nearest_bat(self):
        distance = self.worldx
        for idx, bat in self.sorted_bats.items():
            if bat is not None:
                d = bat.rect.x - self.player.sp.rect.x
                abs_d = abs(d)
                if abs_d < abs(distance):
                    distance = d
        facing_nearest = (distance > 0 and self.player.sp.facing > 0) or (distance < 0 and self.player.sp.facing < 0)
        if facing_nearest and len([x for x in self.sorted_bats.values() if x is not None]) > 0:
            return True
        else:
            return False

    def gameRender(self, custom_message=None, **kwargs):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.running = False
                sys.exit()
        self.world.blit(self.backdrop, self.backdropbox)
        score_surface = self.score_font.render(f"SCORE: {round(self.score * 1000)}, LIVES: {self.lives}", True,
                                               (0, 0, 0, 0))
        self.world.blit(score_surface, (10, 10))
        if custom_message is not None:
            custom_message_surface = self.score_font.render(str(custom_message), True,
                                                            (0, 0, 0, 0))
            self.world.blit(custom_message_surface, (10, 30))
                
        self.player.update()
        self.player_list.draw(self.world)
        self.player_list.draw(self.world)
        pygame.display.flip() #Update the full display Surface to the screen
        self.dt = self.clock.tick_busy_loop(self.fps)
        

        pixl_arr = pygame.surfarray.array2d(self.world)
        pixl_arr = np.swapaxes(pixl_arr, 0, 1)

        # event = Event(self.score, self.lives, self.player, self.worldx, self.worldy, self.sorted_bats, self.max_bats, pixl_arr)
        # self.notify(event)
        return pixl_arr
        