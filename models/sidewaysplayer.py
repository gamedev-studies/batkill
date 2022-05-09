from models.attack import Attack
from models.backend_player import StandardPlayer

MOVE_RIGHT = 'MOVE_RIGHT'
MOVE_LEFT = 'MOVE_LEFT'
JUMP = 'JUMP'
ATTACK = 'ATTACK'


class SideWaysPlayer(StandardPlayer):
    def __init__(self, x, y, ground_y, rect, direction=1, x_step=8, min_x=-20, max_x=855):
        super().__init__(x, y, ground_y, rect, x_step, 0, 0, min_x, max_x)
        self.direction = direction

        self.attack = None

    @property
    def collider_rect(self):
        r = self.rect.inflate(-70, 0)
        r.height -= 20
        r.y += 20
        return r

    def update(self, actions=None):
        self.dx = self.direction * self.x_step
        self.x += self.dx

    def __repr__(self):
        return f'''x: {self.x}, y: {self.y} dx: {self.dx}, dy: {self.dy}, ground: {self.ground_y} attack: {repr(self.attack)}'''


