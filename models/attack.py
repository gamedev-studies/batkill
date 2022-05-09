import pygame


class DamagePoly:
    def __init__(self, x_0, y_0, x_1, y_1, damage):
        self.damage = damage
        if x_0 > x_1:
            temp_x = x_1
            x_1 = x_0
            x_0 = temp_x
        if y_0 > y_1:
            temp_y = y_1
            y_1 = y_0
            y_0 = temp_y
        width = x_1 - x_0
        height = y_1 - y_0
        self.rect = pygame.Rect(x_0, y_0, width, height)


class Attack:
    def __init__(self, player_width, width, height, attack_duration, damage, cool_down_duration):
        self.damage = damage
        self.height = height
        self.width = width
        self.player_width = player_width
        self.attack_poly = None

        self.cool_down_duration = cool_down_duration
        self.cool_down_state = 0

        self.attack_duration = attack_duration
        self.attack_state = 0

    def get_attack_poly(self, attacker_rect, x_direction):
        x_0, y_0 = attacker_rect.topleft
        x_1, y_1 = attacker_rect.bottomright
        if x_direction > 0:
            x_1 += self.width
        else:
            x_0 -= self.width
        return DamagePoly(
            x_0=x_0,
            y_0=y_0,
            x_1=x_1,
            y_1=y_1,
            damage=self.damage
        )

    def perform(self, attacker_rect, x_direction):
        if self.cool_down_state == 0 and self.attack_state == 0:
            self.attack_state = self.attack_duration
            self.attack_poly = self.get_attack_poly(attacker_rect, x_direction)

    def update(self, attacker_rect, x_direction):
        if self.cool_down_state > 0:
            self.cool_down_state -= 1
        if self.attack_state > 0:
            self.attack_state -= 1
            if self.attack_state == 0:
                self.cool_down_state = self.cool_down_duration
                self.attack_poly = None
            # else:
            #     self.attack_poly = self.get_attack_poly(attacker_rect, x_direction)

    def __repr__(self):
        return f"duration: {self.attack_state}, cooldown: {self.cool_down_state} {repr(self.attack_poly)}"
