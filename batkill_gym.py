import gym
import numpy as np

from batkill_game import Command, Observer, Batkill
from gym import spaces
from models.backend_player import MOVE_LEFT, MOVE_RIGHT, JUMP, ATTACK

class BatkillEnv(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, max_bats=2, bat_speed=6, attack_cooldown=10, jump=False) -> None:
        self.game = Batkill(max_bats=max_bats, 
                bat_speed=bat_speed, 
                attack_cooldown=attack_cooldown,
                jump=jump)
        self.observer = Observer()
        self.game.attach(self.observer)
        
    def reset(self):
        self.game.initializeValues()

        self.observation_space_dct = {
            'player_x': spaces.Box(-1, 1, shape=(1,)),
            'player_y': spaces.Box(-1, 1, shape=(1,)),
            'player_direction': spaces.Box(-1, 1, shape=(1,)),
            'player_attack': spaces.Box(-1, 1, shape=(1,)),
            'player_cooldown': spaces.Box(-1, 1, shape=(1,))
        }
        for idx in range(self.observer.event.max_bats):
            self.observation_space_dct[f'bat_{idx}_alive'] = spaces.Box(-1, 1, dtype=np.int16, shape=(1,))
            self.observation_space_dct[f'bat_{idx}_direction'] = spaces.Box(-1, 1, dtype=np.int16, shape=(1,))
            self.observation_space_dct[f'bat_{idx}_x'] = spaces.Box(-1, 1, shape=(1,))
            self.observation_space_dct[f'bat_{idx}_speed'] = spaces.Box(0, 100, shape=(1,))
            self.observation_space_dct[f'bat_{idx}_distance_to_player'] = spaces.Box(-1, 1, shape=(1,))
            self.observation_space_dct[f'bat_{idx}_bat_facing_player'] = spaces.Box(-1, 1, shape=(1,))
            self.observation_space_dct[f'bat_{idx}_player_facing_bat'] = spaces.Box(-1, 1, shape=(1,))
            self.observation_space_dct[f'bat_{idx}_in_attack_range'] = spaces.Box(-1, 1, shape=(1,))
        
        self.mins = np.array([x.low[0] for x in self.observation_space_dct.values()])
        self.maxs = np.array([x.high[0] for x in self.observation_space_dct.values()])
        
        self.observation_space = spaces.Box(self.mins, self.maxs, dtype=np.float32)

        if self.game.jump:
            self.action_space = spaces.MultiDiscrete([3, 2, 2])
            self.available_actions = [[None, MOVE_LEFT, MOVE_RIGHT], [None, JUMP], [None, ATTACK]]
        else:
            self.action_space = spaces.MultiDiscrete([3, 2])
            self.available_actions = [[None, MOVE_LEFT, MOVE_RIGHT], [None, ATTACK]]

        self.reward_range = (-float(5), float(5))
        
        return self._get_obs()

    def step(self, action):
        reward = 0
        
        score = self.observer.event.score 
        lives = self.observer.event.lives

        actions_to_return = []
        for idx, i in enumerate(action):
            if round(i) >= 1:
                actions_to_return.append(self.available_actions[idx][i])

        if ATTACK in action:
            self.reward -= 0.1
        if JUMP in action:
            self.reward -= 0.2

        self.done = not self.game.gameUpdate(Command(actions_to_return))      

        if self.observer.event.score != score:
            reward += 5
        if self.observer.event.lives != lives:
            reward -= 5

        # reward if moving towards the bat
        if self.observer.event.moving_towards:
            reward += 0.1

        if self.observer.event.facing_nearest_bat:
            reward += 0.2

        self.reward = reward

        return self._get_obs(), self.reward, self.observer.event.lives < 1, {}

    def render(self, session=None, build=None):
        return self.game.gameRender(session, build)

    def _get_obs(self):
        dct = {
            'player_x': (self.observer.event.player.sp.rect.x / self.observer.event.worldx) * 2 - 1,
            'player_y': (self.observer.event.player.sp.rect.y / self.observer.event.worldy) * 2 - 1,
            'player_direction': self.observer.event.player.sp.facing,
            'player_attack': (self.observer.event.player.sp.attack.attack_state / self.observer.event.player.sp.attack.attack_duration) * 2 - 1,
            'player_cooldown': (self.observer.event.player.sp.attack.cool_down_state / self.observer.event.player.sp.attack.cool_down_duration) * 2 - 1
        }
        for idx, bat in self.observer.event.sorted_bats.items():
            if bat is not None:
                dct[f'bat_{idx}_alive'] = 1
                dct[f'bat_{idx}_direction'] = bat.direction
                dct[f'bat_{idx}_x'] = (bat.rect.x / self.observer.event.worldx) * 2 - 1
                dct[f'bat_{idx}_speed'] = bat.step
                dct[f'bat_{idx}_distance_to_player'] = (bat.rect.x - self.observer.event.player.sp.rect.x)/self.observer.event.worldx
                if bat.direction == -1:
                    if bat.rect.x > self.observer.event.player.sp.rect.x:
                        bat_facing_player = 1
                    else:
                        bat_facing_player = -1
                else:
                    if bat.rect.x < self.observer.event.player.sp.rect.x:
                        bat_facing_player = 1
                    else:
                        bat_facing_player = -1
                if self.observer.event.player.sp.facing == -1:
                    if self.observer.event.player.sp.rect.x > bat.rect.x:
                        player_facing_bat = 1
                    else:
                        player_facing_bat = -1
                else:
                    if self.observer.event.player.sp.rect.x < bat.rect.x:
                        player_facing_bat = 1
                    else:
                        player_facing_bat = -1
                if player_facing_bat > 0:
                    attack_rect = self.observer.event.player.sp.attack.get_attack_poly(self.observer.event.player.sp.rect, self.observer.event.player.sp.facing).rect
                    if (
                            bat.collider_rect and
                            attack_rect.colliderect(bat.collider_rect) and
                            self.observer.event.player.sp.attack.cool_down_state == 0 and
                            self.observer.event.player.sp.attack.attack_state == 0
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
        return np.array([x for x in dct.values()])