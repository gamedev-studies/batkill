import os

from stable_baselines.common.vec_env import DummyVecEnv

from stable_baselines import PPO2
from game import Game
from stable_baselines.common.vec_env.util import obs_space_info


model_storage_dir = 'nn_models'
max_bats = 4
allow_jump = True
baseline_model = PPO2



g = Game(is_ml=True, max_bats=max_bats, allow_jump=allow_jump)
env = DummyVecEnv([lambda: g])
models = [{'file': x, 'steps': int(x.split('_steps')[0].split('_')[-1])} for x in os.listdir(model_storage_dir)]
latest_model = sorted(models, key=lambda x: -x['steps'])[0]['file']
print(models)
print(latest_model)

model = baseline_model.load(os.path.join(model_storage_dir, latest_model), env=env)
obs = env.reset()
while True:
  action, _states = model.predict(obs)
  obs, rewards, done, info = env.step(action)
  env.render(custom_message=latest_model)
  if done:
    models = [{'file': x, 'steps': int(x.split('_steps')[0].split('_')[-1])} for x in os.listdir(model_storage_dir)]
    latest_model = sorted(models, key=lambda x: -x['steps'])[0]['file']
    obs = env.reset()
    model.load(os.path.join(model_storage_dir, latest_model), env=env)
