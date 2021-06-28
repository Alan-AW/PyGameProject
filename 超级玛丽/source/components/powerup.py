import pygame
from .. import setup, tools
from .. import constants as C


def create_powerup(centerx, centery, type):
    return Mushroom(centerx, centery)


class Powerup(pygame.sprite.Sprite):
    def __init__(self, centerx, centery, frame_rects):
        pygame.sprite.Sprite.__init__(self)

        self.frames = []
        self.frame_index = 0
        for frame_rect in frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['item_objects'], *frame_rect, (0,0,0), 2.5))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = centery
        self.origin_y = centery - self.rect.height/2  # 蘑菇长出来之后向上运动的距离


        # 宝箱内蘑菇的各种状态
        self.x_vel = 0
        self.direction = 1  # 运动方向（右）
        self.y_vel = -1  # 长出来的速度
        self.gravity = 1  # 重力加u速度
        self.max_y_vel = 8  # 向上的最大速度

    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_x_collisions(level)
        self.rect.y += self.y_vel
        self.check_y_collisions(level)

        if self.rect.x < 0 or self.rect.y > C.SCREEN_H:
            self.kill()

    def check_x_collisions(self, level):
        sprite = pygame.sprite.spritecollideany(self, level.ground_items_group)
        if sprite:
            if self.direction:  # 龟壳向右
                self.direction = 0
                self.rect.right = sprite.rect.left
            else:
                self.direction = 1
                self.rect.left = sprite.rect.right
            self.x_vel *= -1

    def check_y_collisions(self, level):
        check_group = pygame.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
        sprite = pygame.sprite.spritecollideany(self, check_group)
        if sprite:
            if self.rect.top < sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.y_vel = 0
                self.state = 'walk'

        level.check_while_fall(self)


class Mushroom(Powerup):
    def __init__(self, centerx, centery):
        Powerup.__init__(self, centerx, centery, [(0,0,16,16)])
        self.x_vel = 2
        self.state = 'grow'
        self.name = 'mushroom'

    def update(self, level):
        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.origin_y:  # 蘑菇长出来之后向上运动的距离
                self.state = 'walk'
        elif self.state == 'walk':
            pass
        elif self.state == 'fall':
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.gravity

        if self.state != 'grow':
            self.update_position(level)


class Fireball(Powerup):
    pass


class LifeMushroom(Powerup):
    pass


class Start(Powerup):
    pass
















