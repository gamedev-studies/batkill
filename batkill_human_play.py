import time
import datetime
import csv
import time
import json

from batkill_game import Batkill, Observer, Command

# read the config
with open("config.json") as config_file:
    data = json.loads(config_file.read())

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

    game.gameRender(custom_message='Manual Play')

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
