import pygame
from .. import tools, setup
from .. import constants as C
from . powerup import create_powerup


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, brick_type, group, color=None, name='brick'):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.brick_type = brick_type
        self.group = group
        self.name = name

        bright_frames_rects = [(16, 0, 16, 16), (48, 0, 16, 16)]
        dark_frames_rects = [(16, 0, 16, 16), (48, 0, 16, 16)]

        if not color:
            self.frame_rects = bright_frames_rects
        else:
            self.frame_rects = dark_frames_rects

        self.frames = []
        for frame_rect in self.frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['tile_set'], *frame_rect, (0, 0, 0), C.BRICK_MULTI))

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.state = 'rest'
        self.gravity = C.GRAVITY

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
        pass

    def go_bumped(self):
        self.y_vel = -7
        self.state = 'bumped'

    def bumped(self):  # 宝箱被顶起来的状态
        self.rect.y += self.y_vel
        self.y_vel = self.gravity

        if self.rect.y > self.y + 5:  # 宝箱的向下动态效果
            self.rect.y = self.y  # 宝箱不会下落

            if self.brick_type == 0:
                self.state = 'rest'
            elif self.brick_type == 1:
                self.state = 'open'
            else:
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.brick_type))

    def open(self):
        self.frame_index = 1
        self.image = self.frames[self.frame_index]
