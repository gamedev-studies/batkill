import os
import string
import sys
import numpy as np
import random

import pygame
from models.enemy_generation import random_bat

from models.spriteful_player import Player
from models.backend_player import MOVE_LEFT, MOVE_RIGHT, JUMP, ATTACK

class Event():
    def __init__(self, score, lives, player, worldx, worldy, sorted_bats, max_bats, pixl_arr):
        self.score = score
        self.lives = lives
        self.player = player
        self.worldx = worldx
        self.worldy = worldy
        self.sorted_bats = sorted_bats
        self.max_bats = max_bats
        self.pixl_arr = pixl_arr
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

    def __init__(self, max_bats=2) -> None:
        self._observers = []
        self.max_bats = max_bats
        self.initializeValues()
    
    def initializeValues(self) -> None:
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
        self.player = Player(adventurer_sprites)  # spawn player
        self.player_list = pygame.sprite.Group()
        self.player_list.add(self.player)

        self.score_font = pygame.font.SysFont(os.path.join('static', 'fonts', 'SourceCodePro-Medium.ttf'), 30)
        self.score_surface = self.score_font.render(f"SCORE: {round(self.score * 1000)}, LIVES: {self.lives}", True,
                                                    (0, 0, 0, 0))

        self.enemies = pygame.sprite.Group()
        self.running = True

        event = Event(self.score, self.lives, self.player, self.worldx, self.worldy, self.sorted_bats, self.max_bats, np.array([]))
        self.notify(event)

    def gameInput(self):
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
        return player_actions

    def gameUpdate(self, command: Command) -> bool:

        attained_score = 0

        action = command.keyPressed()

        if action is None:
            action = []
        self.actions = action
        # if ATTACK in action:
        #     reward -= 0.1
        # if JUMP in action:
        #     reward -= 0.2

        self.player.control(action)

        if any([v is None for v in self.sorted_bats.values()]):
            new_bat = random_bat(current_score=self.score, sprite_path=bat_sprite_path)
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
                # if bat.direction == -1:
                    # if bat.rect.x < self.player.sp.rect.x:
                    #     reward += 0.1
                # else:
                    # if bat.rect.x > self.player.sp.rect.x:
                        # reward += 0.1

                if self.player.sp.attack.attack_poly is not None and not bat.dying:
                    killed = self.player.sp.attack.attack_poly.rect.colliderect(bat.collider_rect)
                    if killed:
                        bat.die()
                        attained_score += 1
                        # reward += 5
                if bat.dead or bat.rect.x > self.worldx or bat.rect.x < 0:
                    self.enemies.remove(bat)
                    bat.kill()
                    self.sorted_bats[idx] = None
                    del bat
                elif bat.collider_rect is not None and self.player.sp.collider_rect.colliderect(bat.collider_rect):
                    bat.die()
                    self.lives -= 1
                    # reward -= 5

        self.score += attained_score

        event = Event(self.score, self.lives, self.player, self.worldx, self.worldy, self.sorted_bats, self.max_bats, self.world)
        self.notify(event)

        return True

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
        pygame.display.flip()
        self.clock.tick(self.fps)

        pixl_arr = pygame.surfarray.array2d(self.world)
        pixl_arr = np.swapaxes(pixl_arr, 0, 1)

        # event = Event(self.score, self.lives, self.player, self.worldx, self.worldy, self.sorted_bats, self.max_bats, pixl_arr)
        # self.notify(event)
        return pixl_arr
        