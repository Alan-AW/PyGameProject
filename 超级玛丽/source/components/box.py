import pygame
from .. import tools, setup
from .. import constants as C
from . powerup import create_powerup


class Box(pygame.sprite.Sprite):
    def __init__(self, x, y, box_type, group, name='box'):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.box_type = box_type
        self.group = group
        self.name = name
        self.frame_rects = [
            (384, 0, 16, 16),
            (400, 0, 16, 16),
            (416, 0, 16, 16),
            (432, 0, 16, 16)
        ]

        self.frames = []
        for frame_rect in self.frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['tile_set'], *frame_rect, (0,0,0), C.BRICK_MULTI))

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.state = 'rest'
        self.timer = 0
        self.gravity = C.GRAVITY
        # self.state = 'bumped'
        # self.state = 'open'

    def update(self):
        self.current_time = pygame.time.get_ticks()
        self.handle_states()

    def handle_states(self):
        if self.state == 'rest':
            self.rest()
        elif self.state == 'bumped':
            self.bumped()
        elif self.state == 'open':
            self.open()

    def rest(self):  # 宝箱正常状态
        frame_durations = [400, 150, 150, 50]  # 4帧造型持续时间
        if self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index = (self.frame_index + 1) % 4
            self.timer = self.current_time
        self.image = self.frames[self.frame_index]

    def go_bumped(self):
        self.y_vel = -7
        self.state = 'bumped'

    def bumped(self):  # 宝箱被顶起来的状态
        self.rect.y += self.y_vel
        self.y_vel = self.gravity
        self.frame_index = 3
        self.image = self.frames[self.frame_index]

        if self.rect.y > self.y + 10:
            self.rect.y = self.y  # 宝箱不会下落
            self.state = 'open'

            # 宝箱被顶起之后判断包厢的类型，根据不同的类型出现不同的道具
            # 0--空  1--金币  2--心心  3--蘑菇
            if self.box_type == 1:
                pass
            else:
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.box_type))



    def open(self):  # 宝箱打开的状态
        pass























