from batkill_game import Batkill, Observer, Command

game = Batkill()

myObserver = Observer()
game.attach(myObserver)

game.initializeValues()
while game.running:    

    player_actions = game.gameInput()

    game.gameUpdate(Command(player_actions))

    game.gameRender(custom_message='Manual Play')

    print(myObserver.event.score)
    