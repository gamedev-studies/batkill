from models.attack import Attack

MOVE_RIGHT = 'MOVE_RIGHT'
MOVE_LEFT = 'MOVE_LEFT'
JUMP = 'JUMP'
ATTACK = 'ATTACK'


class StandardPlayer:
    def __init__(self,
                 ground_y,
                 x_step=8,
                 jump_step=10,
                 jump_stages=11,
                 min_x=50,
                 max_x=785,
                 render=True,
                 rect=None,
                 collider_rect=None
                 ):

        self.rect = rect


        self.max_x = max_x
        self.min_x = min_x

        self.dx = 0
        self.dy = 0
        self.x_step = x_step
        self.facing = 1

        self.ground_y = ground_y

        self.jumping = False
        self.falling = False
        self.jump_step = jump_step
        self.jump_stage = 0
        self.jump_max = jump_stages

        self.attack = Attack(width=50, height=60, attack_duration=6, cool_down_duration=10, damage=5, player_width=70)

    @property
    def collider_rect(self):
        r = self.rect.inflate(-70, 0)
        r.height -= 20
        r.y += 20
        return r

    def get_dy(self):
        if self.jumping and self.jump_stage < self.jump_max:
            self.jump_stage += 1
            dy = -self.jump_step
        elif self.jumping and self.jump_stage == self.jump_max:
            self.jump_stage = 0
            dy = 0
            self.jumping = False
            self.falling = True
        elif self.falling and self.rect.y < self.ground_y:
            dy = self.jump_step
        elif self.falling and self.rect.y == self.ground_y:
            dy = 0
            self.falling = False
            self.jumping = False
        elif not self.falling and not self.jumping:
            dy = 0
        return dy

    def update(self, actions=None):
        if actions is None:
            actions = []
        if MOVE_LEFT in actions:
            dx = -self.x_step
            self.facing = -1
        elif MOVE_RIGHT in actions:
            dx = self.x_step
            self.facing = 1
        else:
            dx = 0

        if JUMP in actions and not self.jumping and not self.falling:
            self.jumping = True

        dy = self.get_dy()
        self.rect.x += dx
        if self.rect.x > self.max_x:
            self.rect.x = self.max_x
        elif self.rect.x < self.min_x:
            self.rect.x = self.min_x
        self.rect.y += dy
        self.dx = dx
        self.dy = dy
        self.attack.update(attacker_rect=self.collider_rect, x_direction=self.facing)
        if ATTACK in actions:
            self.attack.perform(attacker_rect=self.collider_rect, x_direction=self.facing)

    def __repr__(self):
        return f'''x: {self.rect.x}, y: {self.rect.y} dx: {self.dx}, dy: {self.dy}, ground: {self.ground_y} attack: {repr(self.attack)}'''


if __name__ == '__main__':
    p = StandardPlayer(0, 0, 0)
