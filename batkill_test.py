import time
import datetime
import csv
import time
import json
import os
from stable_baselines3 import PPO, A2C
import imageio
import numpy as np

from batkill_game import Batkill, Observer, Command
from batkill_gym import BatkillEnv

models_dir = f"ai-models"
logs_dir = f"logs"
results_dir = f"results"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

if not os.path.exists(results_dir):
    os.makedirs(results_dir)

def _save_gif(session, skill, run, test):
    image_name = ''.join([session,'-',skill,'-',test["id"],'-run',str(run),'.gif'])
    imageio.mimsave(
        ''.join([results_dir,'/',image_name]), 
        [np.array(img) for i, img in enumerate(images) if i%2 == 0], 
        fps=29)   

def _save_results(row):
    with open(''.join([results_dir,'/results.csv']), 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')        
        # writer.writerow(["session","skill","run","time","bats","bat_speed","attack_cooldown","jump","score","lives"])
        writer.writerow(row)

with open("config.json") as config_file:
    data = json.loads(config_file.read())

for run in data["run"]:

    if data["session"] == "human":

        for test in data["tests"]:

            game = Batkill(max_bats=test['bats'], 
                    bat_speed=test['bat_speed'], 
                    attack_cooldown=test['attack_cooldown'],
                    jump=test['jump'])

            myObserver = Observer()
            game.attach(myObserver)

            game.initializeValues()

            t_end = time.time() + data['time']
            while time.time() < t_end:

                player_actions = game.gameInput()

                game.gameUpdate(Command(player_actions))

                game.gameRender(custom_message='HUMAN')

    if data["session"] == "ai-train":

        env = BatkillEnv(max_bats=data['bats'], 
                bat_speed=data['bat_speed'], 
                attack_cooldown=data['attack_cooldown'],
                jump=data['jump'])

        myObserver = Observer()
        env.game.attach(myObserver)

        env.reset()

        if data["skill"] == "novice":
            TIMESTEPS = 1000
        if data["skill"] == "professional":
            TIMESTEPS = 1000000
        else:
            exit(0)

        model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logs_dir)
        model.learn(total_timesteps=TIMESTEPS)
        model.save(''.join([models_dir,"/",data["skill"]]))


    if data["session"] == "ai-play":

        for test in data["tests"]:

            env = BatkillEnv(max_bats=test['bats'], 
                    bat_speed=test['bat_speed'], 
                    attack_cooldown=test['attack_cooldown'],
                    jump=test['jump'])

            myObserver = Observer()
            env.game.attach(myObserver)

            obs = env.reset()

            if data["skill"] != "random":
                model = PPO.load(''.join([models_dir,"/",data["skill"]]), env=env)
            
            images = []
            img = env.render(mode='rgb_array')

            t_end = time.time() + data['time']
            while time.time() < t_end:
                images.append(img)

                if data["skill"] == "random":
                    random_action = env.action_space.sample()
                    observation, reward, done, info = env.step(random_action)             
                else:
                    action, _state = model.predict(obs)
                    obs, reward, done, info = env.step(action)

                img = env.render(mode='rgb_array')

                if done:
                    obs = env.reset()
            
            env.reset()

            _save_gif(data["session"],data["skill"],run,test)
            _save_results([str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')),
                data['session'], data['skill'], run, data['time'],
                test['id'], test['bats'], test['bat_speed'], test['attack_cooldown'], test['jump'],
                myObserver.event.score, myObserver.event.lives])
