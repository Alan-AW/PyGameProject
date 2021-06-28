from .. components import info
import pygame
from .. import tools, setup
from .. import constants as C
from .. components import player, stuff, brick, box, enemy
import os
import json



class Level():
    def start(self, game_info):
        self.game_info = game_info
        self.finished = False
        self.next = 'game_over'
        self.info = info.Info('level', self.game_info)
        self.load_map_data()
        self.setup_backgound()
        self.setup_start_positions()
        self.setup_player()
        self.setup_ground_items()
        self.setup_bricks_and_boxes()  # 地图砖块
        self.setup_enemies()
        self.setup_checkpoints()


    def load_map_data(self):
        file_name = 'level_1.json'
        file_path = os.path.join('source/data/maps', file_name)
        with open(file_path) as f:
            self.map_data = json.load(f)

    def setup_backgound(self):
        self.image_name = self.map_data['image_name']
        self.background = setup.GRAPHICS[self.image_name]
        rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background, (int(rect.width*C.BG_MULTI),
                                                                   int(rect.height*C.BG_MULTI)))
        self.background_rect = self.background.get_rect()
        self.game_window = setup.SCREEN.get_rect()
        self.game_ground = pygame.Surface((self.background_rect.width, self.background_rect.height))

    def setup_start_positions(self):
        self.positions = []
        for data in self.map_data['maps']:
            self.positions.append((data['start_x'], data['end_x'], data['player_x'], data['player_y']))
        self.start_x, self.end_x, self.player_x, self.player_y = self.positions[0]

    def setup_player(self):
        self.player = player.Player('mario')
        self.player.rect.x = self.game_window.x + self.player_x
        self.player.rect.bottom = self.player_y

    def setup_ground_items(self):
        self.ground_items_group = pygame.sprite.Group()
        for name in ['ground', 'pipe', 'step']:
            for item in self.map_data[name]:
                self.ground_items_group.add(stuff.Item(item['x'], item['y'], item['width'], item['height'], name))

    def setup_bricks_and_boxes(self):
        self.brick_group = pygame.sprite.Group()
        self.box_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()

        if 'brick' in self.map_data:
            for brick_data in self.map_data['brick']:
                x, y = brick_data['x'], brick_data['y']
                brick_type = brick_data['type']
                if brick_type == 0:
                    if 'brick_num' in brick_data:
                        pass
                    else:
                        self.brick_group.add(brick.Brick(x, y, brick_type, None))
                elif brick_type == 1:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.coin_group))
                else:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.powerup_group))

        if 'box' in self.map_data:
            for box_data in self.map_data['box']:
                x, y = box_data['x'], box_data['y']
                box_type = box_data['type']
                if box_type == 1:
                    self.box_group.add(box.Box(x, y, box_type, self.coin_group))
                else:
                    self.box_group.add(box.Box(x, y, box_type, self.powerup_group))


    def setup_enemies(self):
        self.dying_group = pygame.sprite.Group()
        self.shell_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.enemy_group_dict = {}
        for enemy_group_data in self.map_data['enemy']:
            group = pygame.sprite.Group()
            for enemy_group_id, enemy_list in enemy_group_data.items():
                for enemy_data in enemy_list:
                    group.add(enemy.create_enemy(enemy_data))
                self.enemy_group_dict[enemy_group_id] = group

    def setup_checkpoints(self):
        self.checkpoint_group = pygame.sprite.Group()
        for item in self.map_data['checkpoint']:
            x, y, w, h = item['x'],item['y'],item['width'],item['height'],
            checkpoint_type = item['type']
            enemy_groupid = item.get('enemy_groupid')
            self.checkpoint_group.add(stuff.Checkpoint(x, y, w, h,checkpoint_type, enemy_groupid))



    def update(self, surface, keys):

        self.current_time = pygame.time.get_ticks()
        self.player.update(keys)

        if self.player.dead:
            if self.current_time -self.player.death_timer > 300:
                self.finished = True
                self.update_game_info()
        elif self.is_frozen():
            pass
        else:
            self.update_player_position()
            self.check_checkpoints()
            self.check_if_go_die()
            self.update_game_window()
            self.info.update()
            self.brick_group.update()
            self.box_group.update()
            self.enemy_group.update(self)
            self.dying_group.update(self)
            self.shell_group.update(self)
            self.coin_group.update()
            self.powerup_group.update(self)


        self.draw(surface)

    def is_frozen(self):
        return self.player.state in ['small2big', 'big2small', 'big2fire', 'fire2small']


    def update_player_position(self):
        # x 方向的碰撞
        self.player.rect.x += self.player.x_vel
        if self.player.rect.x < self.start_x:
            self.player.rect.x = self.start_x
        elif self.player.rect.right > self.end_x:
            self.player.rect.right = self.end_x  # 限制人物不会跑到画面之外
        self.check_x_collisions()

        # y 方向的碰撞
        if not self.player.dead:
            self.player.rect.y += self.player.y_vel
            self.check_y_collisions()

    def check_x_collisions(self):
        check_group = pygame.sprite.Group(self.ground_items_group, self.brick_group, self.box_group)
        collided_sprite = pygame.sprite.spritecollideany(self.player, check_group)
        if collided_sprite:
            self.adjust_player_x(collided_sprite)

        if self.player.hurt_immune:  # 判断是否免疫伤害
            return

        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)
        if enemy:
            if self.player.big:
                self.player.state = 'big2small'
                self.player.hurt_immune = True  # 变小的时候伤害免疫
            else:
                self.player.go_die()

        shell = pygame.sprite.spritecollideany(self.player, self.shell_group)
        if shell:
            if shell.state == 'slide':
                self.player.go_die()
            else:
                if self.player.rect.x < shell.rect.x:
                    shell.x_vel = 10
                    shell.rect.x += 40
                    shell.direction = 1
                else:
                    shell.x_vel = -10
                    shell.rect.x -= 40
                    shell.direction = 0
                shell.state = 'slide'
        powerup = pygame.sprite.spritecollideany(self.player, self.powerup_group)
        if powerup:
            powerup.kill()
            if powerup.name == 'mushroom':  # 大蘑菇，准备变身
                self.player.state = 'small2big'


    def check_y_collisions(self):

        ground_item = pygame.sprite.spritecollideany(self.player, self.ground_items_group)
        brick = pygame.sprite.spritecollideany(self.player, self.brick_group)
        box = pygame.sprite.spritecollideany(self.player, self.box_group)
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)

        if brick and box:
            # 优化碰撞检测，距离砖块和宝箱的位置取最近的那个出发顶起的状态
            to_brick = abs(self.player.rect.centerx - brick.rect.centerx)
            to_box = abs(self.player.rect.centerx - box.rect.centerx)
            if to_brick > to_box:
                brick = None
            else:box = None

        if ground_item:
            self.adjust_player_y(ground_item)
        elif brick:
            self.adjust_player_y(brick)
        elif box:
            self.adjust_player_y(box)
        elif enemy:

            if self.player.hurt_immune:  # 免疫伤害状态直接跳过检测
                return

            self.enemy_group.remove(enemy)
            self.dying_group.add(enemy)
            if enemy.name == 'koopa':
                self.shell_group.add(enemy)
            else:
                self.dying_group.add(enemy)

            if self.player.y_vel < 0:
                how = 'bumped'
            else:
                how = 'trampled'  # 踩踏事故的向上起跳事件
                self.player.state = 'jump'
                self.player.rect.bottom = enemy.rect.top
                self.player.y_vel = self.player.jump_vel * 0.8
            enemy.go_die(how)

        self.check_while_fall(self.player)

    def adjust_player_x(self, sprite):
        if self.player.rect.x < sprite.rect.x:
            self.player.rect.right = sprite.rect.left
        else:
            self.player.rect.left = sprite.rect.right
        self.player.x_vel = 0

    def adjust_player_y(self, sprite):
        if self.player.rect.bottom < sprite.rect.bottom:
            self.player.y_vel = 0
            self.player.rect.bottom = sprite.rect.top
            self.player.state = 'walk'
        else:
            self.player.y_vel = 7
            self.player.rect.top = sprite.rect.bottom
            self.player.state = 'fall'

            if sprite.name == 'box':
                if sprite.state == 'rest':
                    sprite.go_bumped()
            if sprite.name == 'brick':
                if sprite.state == 'rest':
                    sprite.go_bumped()

    def check_while_fall(self, sprite):
        sprite.rect.y += 1
        check_ground = pygame.sprite.Group(self.ground_items_group, self.brick_group, self.box_group)
        collided_sprite = pygame.sprite.spritecollideany(sprite, check_ground)
        if not collided_sprite and sprite.state != 'jump' and not self.is_frozen():
            sprite.state = 'fall'
        sprite.rect.y -= 1


    def update_game_window(self):
        third = self.game_window.x + self.game_window.width/3
        if self.player.x_vel > 0 and self.player.rect.centerx > third and self.game_window.right < self.end_x:
            self.game_window.x += self.player.x_vel
            self.start_x = self.game_window.x


    def draw(self, surface):
        self.game_ground.blit(self.background, self.game_window, self.game_window)
        self.game_ground.blit(self.player.image, self.player.rect)

        self.powerup_group.draw(self.game_ground)
        self.brick_group.draw(self.game_ground)
        self.box_group.draw(self.game_ground)
        self.enemy_group.draw(self.game_ground)
        self.dying_group.draw(self.game_ground)
        self.shell_group.draw(self.game_ground)
        self.coin_group.draw(self.game_ground)

        # for enemy_group in self.enemy_group_dict.values():  # 绘制出敌人组
        #     enemy_group.draw(self.game_ground)

        surface.blit(self.game_ground, (0,0), self.game_window)
        self.info.draw(surface)

    def check_checkpoints(self):
        checkpoint = pygame.sprite.spritecollideany(self.player, self.checkpoint_group)
        if checkpoint:
            if checkpoint.checkpoint_type == 0:
                self.enemy_group.add(self.enemy_group_dict[str(checkpoint.enemy_groupid)])
            checkpoint.kill()  # 检查点消失


    def check_if_go_die(self):
        if self.player.rect.y > C.SCREEN_H:
            self.player.go_die()

    def update_game_info(self):
        if self.player.dead:
            self.game_info['lives'] -= 1
        if self.game_info['lives'] == 0:
            self.next = 'game_over'
        else:
            self.next = 'load_screen'
















