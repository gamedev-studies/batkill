from game import Game

if __name__ == '__main__':
    # https://stackoverflow.com/questions/58974034/pygame-and-open-ai-implementation
    game = Game(is_ml=False, max_bats=5)
    game.step(action=[])
    loop = 0
    while game.running: # game loop
        loop += 1
        actions = game.get_actions()
        # actions = [0, 0, 1, 1]
        game.step(action=actions)

        if loop % 1 == 0:
            game.render(custom_message='Manual Play')