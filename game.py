import gym
import pygame
import sys
import os

from gym import spaces
from models.backend_player import MOVE_LEFT, MOVE_RIGHT, JUMP, ATTACK
import numpy as np

from models.enemy_generation import random_bat
from models.spriteful_player import Player

'''
Objects
'''

bat_sprite_path = os.path.join('static', 'sprites', 'Bat')
background = os.path.join('static', 'backgrounds', 'forest', 'background.png')
adventurer_sprites = os.path.join('static', 'sprites', 'adventurer')


class Game(gym.Env):
    worldx = 928
    worldy = 793

    def reset(self):
        self.initialize_values()
        return self._get_obs()

    metadata = {'render.modes': ['human']}

    def __init__(self, is_ml=False, allow_jump=True, max_bats=2):
        self.max_bats = max_bats
        self.is_ml = is_ml
        self.initialize_values()
        observation_space_dct = {
            'player_x': spaces.Box(-1, 1, shape=(1,)),
            'player_y': spaces.Box(-1, 1, shape=(1,)),
            'player_direction': spaces.Box(-1, 1, shape=(1,)),
            'player_attack': spaces.Box(-1, 1, shape=(1,)),
            'player_cooldown': spaces.Box(-1, 1, shape=(1,))
        }
        for idx in range(self.max_bats):
            observation_space_dct[f'bat_{idx}_alive'] = spaces.Box(-1, 1, dtype=np.int16, shape=(1,))
            observation_space_dct[f'bat_{idx}_direction'] = spaces.Box(-1, 1, dtype=np.int16, shape=(1,))
            observation_space_dct[f'bat_{idx}_x'] = spaces.Box(-1, 1, shape=(1,))
            observation_space_dct[f'bat_{idx}_speed'] = spaces.Box(0, 100, shape=(1,))
            observation_space_dct[f'bat_{idx}_distance_to_player'] = spaces.Box(-1, 1, shape=(1,))
            observation_space_dct[f'bat_{idx}_bat_facing_player'] = spaces.Box(-1, 1, shape=(1,))
            observation_space_dct[f'bat_{idx}_player_facing_bat'] = spaces.Box(-1, 1, shape=(1,))
            observation_space_dct[f'bat_{idx}_in_attack_range'] = spaces.Box(-1, 1, shape=(1,))
        mins = np.array([x.low[0] for x in observation_space_dct.values()])
        maxs = np.array([x.high[0] for x in observation_space_dct.values()])

        self.observation_space = spaces.Box(mins, maxs, dtype=np.float32)
        if allow_jump:
            self.action_space = spaces.MultiDiscrete([3, 2, 2])
            self.available_actions = [[None, MOVE_LEFT, MOVE_RIGHT], [None, JUMP], [None, ATTACK]]
        else:
            self.action_space = spaces.MultiDiscrete([3, 2])
            self.available_actions = [[None, MOVE_LEFT, MOVE_RIGHT], [None, ATTACK]]

        self.reward_range = (-float(5), float(5))

    def action_mapper(self, action_array):
        actions_to_return = []
        for idx, i in enumerate(action_array):
            if round(i) >= 1:
                actions_to_return.append(self.available_actions[idx][i])
        return actions_to_return

    def initialize_values(self):
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

    def get_actions(self):

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

    def render(self, custom_message=None, **kwargs):
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

    def _get_obs(self):
        # rect = pygame.Rect(0, 650, self.worldx, self.worldy-700)
        # sub = self.world.subsurface(rect)
        # pygame.image.save(sub, "screenshot.jpg")
        # pixels = pygame.PixelArray(sub)

        dct = {
            'player_x': (self.player.sp.rect.x / self.worldx) * 2 - 1,
            'player_y': (self.player.sp.rect.y / self.worldy) * 2 - 1,
            'player_direction': self.player.sp.facing,
            'player_attack': (self.player.sp.attack.attack_state / self.player.sp.attack.attack_duration) * 2 - 1,
            'player_cooldown': (
                                       self.player.sp.attack.cool_down_state / self.player.sp.attack.cool_down_duration) * 2 - 1
        }
        for idx, bat in self.sorted_bats.items():
            if bat is not None:
                dct[f'bat_{idx}_alive'] = 1
                dct[f'bat_{idx}_direction'] = bat.direction
                dct[f'bat_{idx}_x'] = (bat.rect.x / self.worldx) * 2 - 1
                dct[f'bat_{idx}_speed'] = bat.step
                dct[f'bat_{idx}_distance_to_player'] = (bat.rect.x - self.player.sp.rect.x)/self.worldx
                if bat.direction == -1:
                    if bat.rect.x > self.player.sp.rect.x:
                        bat_facing_player = 1
                    else:
                        bat_facing_player = -1
                else:
                    if bat.rect.x < self.player.sp.rect.x:
                        bat_facing_player = 1
                    else:
                        bat_facing_player = -1
                if self.player.sp.facing == -1:
                    if self.player.sp.rect.x > bat.rect.x:
                        player_facing_bat = 1
                    else:
                        player_facing_bat = -1
                else:
                    if self.player.sp.rect.x < bat.rect.x:
                        player_facing_bat = 1
                    else:
                        player_facing_bat = -1
                if player_facing_bat > 0:
                    attack_rect = self.player.sp.attack.get_attack_poly(self.player.sp.rect, self.player.sp.facing).rect
                    if (
                            bat.collider_rect and
                            attack_rect.colliderect(bat.collider_rect) and
                            self.player.sp.attack.cool_down_state == 0 and
                            self.player.sp.attack.attack_state == 0
                    ):
                        bat_in_range = 1
                    else:
                        bat_in_range = -1
                else:
                    bat_in_range = -1

                dct[f'bat_{idx}_bat_facing_player'] = bat_facing_player
                dct[f'bat_{idx}_player_facing_bat'] = player_facing_bat
                dct[f'bat_{idx}_in_attack_range'] = bat_in_range

            else:
                dct[f'bat_{idx}_alive'] = -1
                dct[f'bat_{idx}_direction'] = 0
                dct[f'bat_{idx}_x'] = -1
                dct[f'bat_{idx}_speed'] = 0
                dct[f'bat_{idx}_distance_to_player'] = 0
                dct[f'bat_{idx}_bat_facing_player'] = 0
                dct[f'bat_{idx}_player_facing_bat'] = 0
                dct[f'bat_{idx}_in_attack_range'] = 0
        if self.is_ml:
            return np.array([x for x in dct.values()])
        else:
            return dct

    def check_facing_nearest_bat(self):
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


    def step(self, action):
        self.loop += 1
        reward = 0
        attained_score = 0
        if self.is_ml:
            action = self.action_mapper(action)

        if action is None:
            action = []
        self.actions = action
        if ATTACK in action:
            reward -= 0.1
        if JUMP in action:
            reward -= 0.2

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
                if bat.direction == -1:
                    if bat.rect.x < self.player.sp.rect.x:
                        reward += 0.1
                else:
                    if bat.rect.x > self.player.sp.rect.x:
                        reward += 0.1

                if self.player.sp.attack.attack_poly is not None and not bat.dying:
                    killed = self.player.sp.attack.attack_poly.rect.colliderect(bat.collider_rect)
                    if killed:
                        bat.die()
                        reward += 5
                        attained_score += 1
                if bat.dead or bat.rect.x > self.worldx or bat.rect.x < 0:
                    self.enemies.remove(bat)
                    bat.kill()
                    self.sorted_bats[idx] = None
                    del bat
                elif bat.collider_rect is not None and self.player.sp.collider_rect.colliderect(bat.collider_rect):
                    bat.die()
                    self.lives -= 1
                    reward -= 5



        if self.check_facing_nearest_bat():
            reward += 0.2

        self.score += attained_score
        self.reward = reward

        return self._get_obs(), reward, self.lives < 1, {}

# when play.py is called this function is never active
if __name__ == '__main__':
    # https://stackoverflow.com/questions/58974034/pygame-and-open-ai-implementation
    game = Game(is_ml=False)
    game.step(action=[])
    loop = 0
    while game.running:
        loop += 1
        actions = game.get_actions()
        # actions = [0, 0, 1, 1]
        game.step(action=actions)

        if loop % 1 == 0:
            game.render()
