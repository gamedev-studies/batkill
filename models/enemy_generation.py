import random

from models.spriteful_bat import Bat


def deterministic_bat(sprite_path, current_score, loop, frequency=100, base_speed=6):
    current_score = 0 if current_score < 0 else current_score
    speed = int(base_speed * (1 + current_score / 20))
    if loop % frequency == 0:
        return Bat(direction=random.choice([-1, 1]), step=speed, sprite_path=sprite_path)
    else:
        return None


def random_bat(sprite_path, current_score, base_prob=50, base_speed=6):
    current_score = 0 if current_score < 0 else current_score
    current_odds = base_prob - current_score / 15
    speed = int(base_speed * (1 + current_score / 20))
    if (random.random() * current_odds) + 1 > current_odds:
        return Bat(direction=random.choice([-1, 1]), step=speed, sprite_path=sprite_path)
    else:
        return None