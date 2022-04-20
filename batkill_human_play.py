from time import time
from batkill_game import Batkill, Observer, Command
import csv
import time

# testing session params
TIME = 30 # seconds
RUN = 'run1'
SKILL = 'novice' # profissional

# testing session game params
BATS = 2
BAT_SPEED = 6 # default 6
ATTACK_COOLDOWN = 20 # default 10
JUMP = False

game = Batkill(max_bats=BATS, bat_speed=BAT_SPEED, attack_cooldown=ATTACK_COOLDOWN, jump=JUMP)

myObserver = Observer()
game.attach(myObserver)

game.initializeValues()

t_end = time.time() + TIME
while time.time() < t_end:

    player_actions = game.gameInput()

    game.gameUpdate(Command(player_actions))

    game.gameRender(custom_message='Manual Play')

    print(myObserver.event.sorted_bats)

    with open(''.join(['results/human-',SKILL,'-',RUN,'.csv']), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)        
        writer.writerow(['enemies', BATS])
        writer.writerow(['enemy_speed', BAT_SPEED])
        writer.writerow(['jump', JUMP])
        writer.writerow(['attack_cooldown', ATTACK_COOLDOWN])
        writer.writerow(['score', myObserver.event.score])
        writer.writerow(['lives', myObserver.event.lives])