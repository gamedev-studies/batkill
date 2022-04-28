import time
import datetime
import csv
import time
import json
import os
from stable_baselines3 import PPO
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

def _save_gif(images, session, skill, run, test):
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

            # images = []
            # img = game.gameRender(session=data["session"], build=test["id"])

            t_end = time.time() + data['time']
            while time.time() < t_end:
                # images.append(img)    

                player_actions = game.gameInput()

                game.gameUpdate(Command(player_actions))

                game.gameRender(session=data["session"], build=test["id"])                

            delta = myObserver.event.score + myObserver.event.lives
            
            # save the results only after warming up
            if not data["warmup"]:
                # _save_gif(images, data["session"],data["skill"],run,test)
                _save_results([str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')),
                    data['time'], run, data['session'], data['skill'],
                    test['id'], test["train"], test['bats'], test['bat_speed'], test['attack_cooldown'], test['jump'],
                    myObserver.event.score, myObserver.event.lives, delta])


    if data["session"] == "ai-train":

        # no need to train twice
        if run == 2:
            break

        for test in data["tests"]:
            # only train the first and last build
            if (test['train']):         

                env = BatkillEnv(max_bats=test['bats'], 
                        bat_speed=test['bat_speed'], 
                        attack_cooldown=test['attack_cooldown'],
                        jump=test['jump'])

                myObserver = Observer()
                env.game.attach(myObserver)

                env.reset()

                if data["skill"] == "novice":
                    TIMESTEPS = 100000
                if data["skill"] == "pro":
                    TIMESTEPS = 1000000                

                model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logs_dir)
                model.learn(total_timesteps=TIMESTEPS)
                model.save(''.join([models_dir,"/",data["skill"],'-',test["id"]]))


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
                if test["train"]:
                    model_name = ''.join([models_dir,"/",data["skill"],'-',test["id"]])                    
                else:
                    model_name = ''.join([models_dir,"/",data["skill"],'-build-2'])

                model = PPO.load(model_name, env=env)
            
            # images = []
            # img = env.render(session=data["session"], build=test["id"])

            t_end = time.time() + data['time']
            while time.time() < t_end:
                # images.append(img)

                if data["skill"] == "random":
                    random_action = env.action_space.sample()
                    observation, reward, done, info = env.step(random_action)             
                else:
                    action, _state = model.predict(obs)
                    obs, reward, done, info = env.step(action)

                env.render(session=data["session"], build=test["id"])
                
                # if done:
                #     obs = env.reset()
            
            delta = myObserver.event.score + myObserver.event.lives

            # _save_gif(images, data["session"],data["skill"],run,test)
            _save_results([str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')),
                data['time'], run, data['session'], data['skill'],
                test['id'], test["train"], test['bats'], test['bat_speed'], test['attack_cooldown'], test['jump'],
                myObserver.event.score, myObserver.event.lives, delta])

            env.reset()