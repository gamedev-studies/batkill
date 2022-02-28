import time
from stable_baselines3 import PPO, A2C
from batkill_gym import BatkillEnv
import os

models_dir = "ppo"
logdir = f"logs"

if not os.path.exists(models_dir):
	os.makedirs(models_dir)

if not os.path.exists(logdir):
	os.makedirs(logdir)

env = BatkillEnv()
env.reset()

TIMESTEPS = 100000

model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logdir)
model.learn(total_timesteps=TIMESTEPS)
model.save(f"{models_dir}/{TIMESTEPS}")




# img = model.env.render(mode='rgb_array')
# imageio.mimsave('lander_a2c.gif', [np.array(img) for i, img in enumerate(images) if i%2 == 0], fps=29)