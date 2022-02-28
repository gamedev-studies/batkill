from stable_baselines.common import make_vec_env
from stable_baselines.common.callbacks import CheckpointCallback
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2
from game import Game
import datetime
import os


model_storage_dir = 'nn_models'
max_bats = 4
allow_jump = True
timestep_checkpoint = 20000
total_time_steps = 2000000000
baseline_model = PPO2
baseline_policy = MlpPolicy
verbosity = 1


timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H%M')
checkpoint_callback = CheckpointCallback(save_freq=timestep_checkpoint, save_path='./nn_models/',
                                         name_prefix=timestamp)
if not os.path.exists(model_storage_dir):
    os.makedirs(model_storage_dir)

g = Game(is_ml=True, max_bats=max_bats, allow_jump=allow_jump)
def make_game():
    return Game(is_ml=True, max_bats=max_bats, allow_jump=allow_jump)

if __name__ == '__main__':
    num_cpu = 4
    # env = DummyVecEnv([lambda: g])
    env = make_vec_env(make_game, 4)
    model = baseline_model(baseline_policy, env, verbose=verbosity)
    model.learn(total_time_steps, callback=checkpoint_callback)
