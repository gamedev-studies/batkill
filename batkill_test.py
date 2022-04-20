import time
import datetime
import csv
import time
import json
import os
from stable_baselines3 import PPO, A2C

from batkill_game import Batkill, Observer, Command
from batkill_gym import BatkillEnv

# read the config
with open("config.json") as config_file:
    data = json.loads(config_file.read())

if data["session"] == "human":
    game = Batkill(max_bats=data['bats'], 
               bat_speed=data['bat_speed'], 
               attack_cooldown=data['attack_cooldown'],
               jump=data['jump'])

    myObserver = Observer()
    game.attach(myObserver)

    game.initializeValues()

    t_end = time.time() + data['time']
    while time.time() < t_end:

        player_actions = game.gameInput()

        game.gameUpdate(Command(player_actions))

        game.gameRender(custom_message='HUMAN')

if data["session"] == "ai-train":
    models_dir = "ppo"
    logdir = f"logs"

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    if not os.path.exists(logdir):
        os.makedirs(logdir)

    env = BatkillEnv(max_bats=data['bats'], 
               bat_speed=data['bat_speed'], 
               attack_cooldown=data['attack_cooldown'],
               jump=data['jump'])

    myObserver = Observer()
    env.game.attach(myObserver)

    env.reset()

    if data["skill"] == "novice":
        TIMESTEPS = 1000
    else:
        TIMESTEPS = 1000000

    model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logdir)
    model.learn(total_timesteps=TIMESTEPS)
    model.save(f"{models_dir}/{TIMESTEPS}")


if data["session"] == "ai-play":
    pass

if data["session"] == "human" or data["session"] == "ai-play":
    # print the results
    with open(''.join(['results.csv']), 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')        
        # writer.writerow(["session","skill","run","time","bats","bat_speed","attack_cooldown","jump","score","lives"])
        writer.writerow([str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')),
            data['session'],
            data['skill'],
            data['run'],
            data['time'],
            data['bats'],
            data['bat_speed'],
            data['attack_cooldown'],
            data['jump'],
            myObserver.event.score,
            myObserver.event.lives])
