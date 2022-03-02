import os
import imageio
import numpy as np

from stable_baselines3 import PPO, A2C

from batkill_gym import BatkillEnv

for x in os.listdir("ppo/"):
    model_dir = os.path.join("ppo/",x)
    break

env = BatkillEnv()
obs = env.reset()

model = PPO.load(model_dir, env=env)

iters = 0

images = []
img = model.env.render(mode='rgb_array')
for i in range(300):
    iters += 1
    print("iteration", iters)

    # random actions  
    # random_action = env.action_space.sample()
    # observation, reward, done, info = env.step(random_action) 

    images.append(img)
    
    action, _state = model.predict(obs)
    obs, reward, done, info = env.step(action)
    img = model.env.render(mode='rgb_array')

    if done:
        obs = env.reset()

# imageio.mimsave('batkill_ppo.gif', [np.array(img) for i, img in enumerate(images) if i%2 == 0], fps=29)