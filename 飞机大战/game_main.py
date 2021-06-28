'''
游戏核心模块
'''

import pygame
from game_hub import *
from game_items import *
import random


class Game():
    '''游戏核心类'''
    def __init__(self):
        # 游戏窗口
        self.min_window = pygame.display.set_mode(SCREEN_RECT.size)

        # 游戏状态
        self.is_game_over = False
        self.is_game_pause = False

        # 游戏精灵组
        self.all_group = pygame.sprite.Group()  # 存放所有界面上的精灵
        self.enemies_group = pygame.sprite.Group()  # 敌机
        self.supplies_group = pygame.sprite.Group()  # 道具

        # 游戏精灵

        # Background(False, self.all_group)  # 背景星空精灵
        # Background(True, self.all_group)  # 背景星空精灵

        # 简化上面两行代码--手动添加到精灵组里面去，不初始化
        self.all_group.add(Background(False), Background(True))

        # 创建游戏控制面板
        self.hub_panel = HUDPanel(self.all_group)

        # 创建玩家飞机精灵--用列表推导式传入玩家飞机图片
        # self.hero_sprite = Plane(['me%d.png' % i for i in range(1,3)],
        self.hero_sprite = Hero(self.all_group)
        self.hub_panel.show_bomb(self.hero_sprite.bomb_count)

        # 初始化敌机
        self.create_enemies()



        # '''测试让敌机静止显示，用玩家飞机去检测碰撞'''
        # for enemy in self.enemies_group.sprites():
        #     enemy.speed = 0  # 敌机速度
        #     enemy.rect.y += 400  # 敌机间距
        # self.hero_sprite.speed = 2  # 玩家飞机速度

        # 创建道具
        self.create_supply()

        # 背景音乐
        # pygame.mixer.music.load('./images/bg.wav')
        # pygame.mixer.music.play(-1)


    def reset_game(self):
        '''重置游戏数据'''
        self.is_game_over = False
        self.is_game_pause = True

        # 重置面板
        self.hub_panel.reset_panel()

        # 重置玩家飞机位置
        self.hero_sprite.rect.midbottom = HERO_DEFAULT_MID_BOTTOM

        # 销毁所有的敌机
        for enemy in self.enemies_group:
            enemy.kill()

        # 销毁子弹
        for bullet in self.hero_sprite.bullets_group:
            bullet.kill()

        # 从新创建飞机
        self.create_enemies()


    def start(self):
        '''开启游戏主要的逻辑'''
        # 创建时钟
        clock = pygame.time.Clock()
        # 动画帧数计数器
        frame_count = 0

        while True:

            # 判断玩家是否已经死亡
            self.is_game_over = self.hub_panel.lives_count == 0

            # 处理事件监听
            if self.event_handler():
                # event_handler  返回  True，就说明发生了退出事件
                return

            # ----------测试--------根据游戏状态模拟切换界面显示内容
            if self.is_game_over:
                # print('结束')
                self.hub_panel.panel_paused(True, self.all_group)
            elif self.is_game_pause:
                # print('暂停')
                self.hub_panel.panel_paused(False, self.all_group)
            else:
                # 游戏进行中，
                # print('进行中...')
                self.hub_panel.panel_resum(self.all_group)

                # 处理长按事件--玩家飞机的移动
                keys = pygame.key.get_pressed()  # get_pressed()得到一个元组

                # 测试代码
                # if keys[pygame.K_RIGHT]:  # 每一个按键在元组里都有一个唯一下标，对应下标值为1则说明按键被按下
                #     self.hero_sprite.rect.x += 10
                # elif keys[pygame.K_LEFT]:
                #     self.hero_sprite.rect.x -= 10
                # elif keys[pygame.K_UP]:
                #     self.hero_sprite.rect.y -= 10
                # elif keys[pygame.K_DOWN]:
                #     self.hero_sprite.rect.y -= 10


                # 简化以上按键处理
                move_hor = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                move_ver = keys[pygame.K_DOWN] - keys[pygame.K_UP]

                # 检测碰撞
                self.check_collide()


                # 这是测试代码，自动加分
                # if self.hub_panel.increase_score(100):
                #     print('升级到了%d' %self.hub_panel.level)
                #     self.create_enemies()
                # 这个是减少血量的效果
                # # self.hero_sprite.hp -= 1

                # 背景图片移动起来（更新）
                self.all_group.update(frame_count == 0, move_hor, move_ver)

                # 绘制精灵图片
            self.all_group.draw(self.min_window)

                # 减少飞机动画帧率
            frame_count = (frame_count + 1) % FRAME_INTERVAL

                # 刷新界面
            pygame.display.update()

                # 设置刷新率--60帧
            clock.tick(60)

    def event_handler(self):
        '''获取并处理事件'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 退出按钮被点击--也就是窗口的 X

                # 退出游戏之前保存最好成绩
                self.hub_panel.save_best_score()

                return True

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # 按下了esc键，退出
                return True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # 按下了空格键
                if self.is_game_over:
                    # 游戏已经结束， 重置游戏
                    self.reset_game()
                else:
                    # 游戏还没有结束， 切换暂停状态----取反
                    self.is_game_pause = not self.is_game_pause




            # 必须在游戏没有暂停才能执行的操作
            if not self.is_game_over and not self.is_game_pause:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    # 释放一个炸弹，并且修改炸弹数量
                    score = self.hero_sprite.blowup(self.enemies_group)
                    self.hub_panel.show_bomb(self.hero_sprite.bomb_count)
                    if self.hub_panel.increase_score(score):
                        self.create_enemies()

                elif event.type == HERO_DEAD_EVENT:
                    # 玩家飞机死亡
                    self.hub_panel.lives_count -= 1
                    self.hub_panel.show_lives()
                    self.hub_panel.show_bomb(self.hero_sprite.bomb_count)
                elif event.type == HERO_POWER_OFF_EVENT:
                    # 无敌时间结束
                    self.hero_sprite.is_power = False
                    pygame.time.set_timer(HERO_POWER_OFF_EVENT, 0)  # 设置定时器延时为0，可以取消定时器
                elif event.type == HERO_FIRE_EVENT:
                    # 英雄飞机发射子弹定时事件
                    self.hero_sprite.fire(self.all_group)
                elif event.type == THROW_SUPPLY_EVENT:
                    # 随机一个道具
                    supply = random.choice(self.supplies_group.sprites())  # 随机选一个出来
                    supply.throw_supply()
                elif event.type == BULLET_ENHANCED_OFF_EVENT:
                    # 玩家使用双排子弹的时间结束，回复为单排
                    self.hero_sprite.bullets_kind = 0  # 回复单排子弹
                    pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 0)  # 取消定时

        return False


    def create_enemies(self):
        '''创建敌机'''
        count = len(self.enemies_group.sprites())
        groups = (self.all_group, self.enemies_group)

        # 根据不同的关卡创建不同的敌机
        if self.hub_panel.level == 1 and count == 0:
            # 关卡1
            for i in range(16):
                Enemy(0, 3, *groups)
        elif self.hub_panel.level == 2 and count == 16:
            # 关卡2
            for enemy in self.enemies_group.sprites():
                enemy.max_speed = 5
            for i in range(8):
                Enemy(0, 5, *groups)
            for i in range(2):
                Enemy(1, 1, *groups)
        elif self.hub_panel.level == 3 and count == 26:
            for enemy in self.enemies_group.sprites():
                enemy.max_speed = 7 if enemy.kind == 0 else 3
            for i in range(8):
                Enemy(0, 7, *groups)
            for i in range(2):
                Enemy(1, 3, *groups)
            for i in range(2):
                Enemy(2, 1, *groups)

    def check_collide(self):
        '''检查是否碰撞'''
        if not self.hero_sprite.is_power:  # 没有无敌才需要检查碰撞
            collide_enemies = pygame.sprite.spritecollide(self.hero_sprite,
                                                          self.enemies_group,
                                                          False,
                                                          pygame.sprite.collide_mask)

            # 过滤掉已经炸毁的敌机--玩家飞机撞到残骸的时候不会发生碰撞
            collide_enemies = list(filter(lambda x: x.hp > 0, collide_enemies))

            # 撞毁玩家飞机
            if collide_enemies:
                self.hero_sprite.hp = 0

            # 撞毁敌机
            for enemy in collide_enemies:
                enemy.hp = 0

            # 子弹和敌机的碰撞分析
            hit_enemies = pygame.sprite.groupcollide(self.enemies_group, self.hero_sprite.bullets_group,
                                                     False, False, pygame.sprite.collide_mask)

            for enemy in hit_enemies:
                # 已经被摧毁的敌机不需要再处理了
                if enemy.hp <= 0:
                    continue

                for bullet in hit_enemies[enemy]:
                    bullet.kill()  # 销毁子弹
                    enemy.hp -= bullet.damage  # 扣血

                    if enemy.hp > 0:  # 判断敌机是否被销毁，没有的话就遍历下一个子弹
                        continue
                    # 敌机被当前子弹销毁
                    if self.hub_panel.increase_score(enemy.value):  # 升级
                        self.create_enemies()  # 加分
                        # 敌机被摧毁就不用再看下一课子弹了
                    break

        # 检查玩家飞机和道具的碰撞
        supplies = pygame.sprite.spritecollide(self.hero_sprite, self.supplies_group,
                                               False, pygame.sprite.collide_mask)

        if supplies:
            supply = supplies[0]

            # 根据道具类型产生不同的行为
            if supply.kind == 0:
                self.hero_sprite.bomb_count += 1
                self.hub_panel.show_bomb(self.hero_sprite.bomb_count)
            else:
                self.hero_sprite.bullets_kind = 1  # 修改子弹为双排
                pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 10000)  # 双排子弹10秒持续时间

            # 移动道具到屏幕最下方
            supply.rect.y = SCREEN_RECT.h


    def create_supply(self):
        '''初始化两个道具，开启刷新投放道具的定时器'''
        Supply(0, self.all_group, self.supplies_group)
        Supply(1, self.all_group, self.supplies_group)

        pygame.time.set_timer(THROW_SUPPLY_EVENT, 10000)  # 10秒丢一个道具









if __name__ == '__main__':
    # 实际操作的时候需要初始化
    pygame.init()
    # 开始游戏
    Game().start()
    # 释放资源
    pygame.quit()
