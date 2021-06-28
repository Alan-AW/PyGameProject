'''
游戏元素模块
'''

import pygame
pygame.init()
import random

# 定义全局变量
SCREEN_RECT = pygame.Rect(0, 0, 480, 700)  # 游戏的窗口矩形大小
FRAME_INTERVAL = 10  # 减少飞机动画帧率
HERO_BOMB_COUNT = 3  # 默认炸弹数量
HERO_DEFAULT_MID_BOTTOM = (SCREEN_RECT.centerx,
                           SCREEN_RECT.bottom - 90)  # 玩家飞机默认位置
HERO_DEAD_EVENT = pygame.USEREVENT  # 玩家飞机销毁事件
HERO_POWER_OFF_EVENT = pygame.USEREVENT + 1  # 取消玩家飞机无敌事件
HERO_FIRE_EVENT = pygame.USEREVENT + 2  # 飞机发射子弹事件
THROW_SUPPLY_EVENT = pygame.USEREVENT + 3  # 投放道具事件
BULLET_ENHANCED_OFF_EVENT = pygame.USEREVENT + 4  # 关闭子弹增强事件


class GameSprite(pygame.sprite.Sprite):
    res_path = './image/'

    def __init__(self, image_name, speed, *group):
        '''初始化精灵对象'''
        # 调用父类方法，把当前精灵对象放到精灵组里面
        super(GameSprite, self).__init__(*group)

        # 创建图片--self.image 不可改动
        self.image = pygame.image.load(self.res_path + image_name)

        # 获取矩形
        self.rect = self.image.get_rect()

        # 设置移动速度
        self.speed = speed

        # 生成遮罩属性提高碰撞检测的执行效率
        self.mask = pygame.mask.from_surface(self.image)


    def update(self, *args):
        '''跟新元素内容数据'''
        self.rect.y += self.speed

class Background(GameSprite):

    def __init__(self, is_alt, *group):
        '''如果is_alt 为True 则初始化时这个精灵显示在窗口上方，'''
        super(Background, self).__init__('background.png', 2, *group)

        if is_alt:
            self.rect.y = -self.rect.h

    def update(self, *args):
        super(Background, self).update(*args)
        # 如果图片已经跑到窗口底部，则立即回到窗口的做上面重新开始滚动
        if self.rect.y > self.rect.h:
            self.rect.y = -self.rect.y


class StatusButton(GameSprite):

    def __init__(self, image_names, *groups):
        '''images_names 接受一个元组，元组的0下标必须是暂停的图片， 1下标必须是运行的图片'''
        super(StatusButton, self).__init__(image_names[0], 0, *groups)

        # 准备用于切换显示的两张图片
        self.images = [pygame.image.load(self.res_path+name) for name in image_names]

    def swicth_status(self, is_pause):
        '''根据是否暂停，切换要使用的图片对象'''
        self.image = self.images[1 if is_pause else 0]


class Label(pygame.sprite.Sprite):
    '''标签精灵类'''
    font_path = './fontt/MarkerFelt.ttc'

    def __init__(self, text, size, color, *groups):
        '''初始化标签精灵的数据'''
        super(Label, self).__init__(*groups)

        # 创建字体对象
        self.font = pygame.font.Font(self.font_path, size)

        # 字体的颜色
        self.color = color

        # 精灵属性
        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()

    def set_text(self, text):
        '''跟新显示文本内容  从新渲染一次'''
        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()


class Plane(GameSprite):
    '''飞机精灵类'''
    def __init__(self, normal_names, speed, hp, value, wav_name, hurt_name, destroy_names, *groups):
        '''飞机类的初始化'''
        super(Plane, self).__init__(normal_names[0], speed, *groups)

        # 飞机基本属性
        self.hp = hp  # 当前生命值
        self.max_hp = hp  # 初始生命
        self.value = value  # 分值
        self.wav_name = wav_name  # 音效

        #飞机要显示的图片
        self.normal_images = [pygame.image.load(self.res_path + name) for name in normal_names]  # 正常状态图像列表
        self.normal_index = 0  # 正常状态图像索引
        self.hurt_image = pygame.image.load(self.res_path + hurt_name)  # 受伤图像
        self.destroy_images = [pygame.image.load(self.res_path + name) for name in destroy_names]  # 摧毁状态图像列表o
        self.destroy_index = 0  # 摧毁状态的索引

    def reset_plan(self):
        '''重置飞机'''
        self.hp = self.max_hp  # 生命值

        self.normal_index = 0  # 正常状态索引
        self.destroy_index = 0  # 被摧毁状态索引

        self.image = self.normal_images[0]  # 恢复正常图像


    def update(self, *args):
        '''更新状态，准备下一次要显示的内容'''

        # 判断是否要更新
        # 减少飞机动画帧率
        if not args[0]:
            return

        if self.hp == self.max_hp:
            # 切换要显示的图片
            self.image = self.normal_images[self.normal_index]
            # 计算下一次显示的索引
            count = len(self.normal_images)
            self.normal_index = (self.normal_index + 1) % count
        elif self.hp > 0:
            # 受伤
            self.image = self.hurt_image
        else:
            # 死亡
            if self.destroy_index < len(self.destroy_images):
                self.image = self.destroy_images[self.destroy_index]
                self.destroy_index += 1
            else:
                self.reset_plan()


class Enemy(Plane):
    '''敌机'''
    def __init__(self, kind, max_speed, *groups):
        '''初始化敌机'''
        self.kind = kind
        self.max_speed = max_speed
        if kind == 0:
            # 小敌机
            super(Enemy, self).__init__(
                ['enemy1.png'], 1, 3, 1000, 'boom.wav',
                'enemy1.png',
                ['enemy1_down%d.png' % j for j in range(1, 5)],
                *groups
            )

        elif kind == 1:
            # 中敌机
            super(Enemy, self).__init__(
                ['enemy2.png'], 1, 9, 5000, 'boom.wav',
                'enemy2_hit.png',
                ['enemy2_down%d.png' % j for j in range(1, 5)],
                *groups
            )

        elif kind == 2:
            # 大敌机
            super(Enemy, self).__init__(
                ['enemy3_n1.png', 'enemy3_n2.png'], 1, 15, 10000, 'boom.wav',
                'enemy3_n1.png',
                ['enemy3_down%d.png' % j for j in range(1, 7)],
                *groups
            )


        # 初始化飞机时，让飞机随机选择一个位置显示
        self.reset_plan()


    def reset_plan(self):
        '''重置敌机'''
        super(Enemy, self).reset_plan()

        # 敌机数据重置
        x = random.randint(0, SCREEN_RECT.w - self.rect.w)
        y = random.randint(0, SCREEN_RECT.h - self.rect.h) - SCREEN_RECT.h

        self.rect.topleft = (x, y)

        # 设置初始速度
        self.speed = random.randint(1, self.max_speed)


    def update(self, *args):
        '''更新飞机的位置信息'''
        super(Enemy, self).update(*args)

        # 根据血量判断是否还要移动
        if self.hp > 0:
            self.rect.y += self.speed

        # 如果移动后已经到了品屏幕之外。需要从新使用
        if self.rect.y >= SCREEN_RECT.h:
            self.reset_plan()


class Hero(Plane):
    '''玩家飞机类'''
    def __init__(self, *groups):
        '''初始化玩家飞机'''
        self.is_power = False  # 是否无敌
        self.bomb_count = HERO_BOMB_COUNT  # 炸弹数量
        self.bullets_kind = 0  # 默认子弹类型
        self.bullets_group = pygame.sprite.Group()  # 子弹精灵组

        super(Hero, self).__init__(
            ('me1.png', 'me2.png'),
            5, 1, 0, 'boom.wav', 'me1.png',
            ['me_destroy_%d.png' % x for x in range(1, 5)],
            *groups)

        self.rect.midbottom = HERO_DEFAULT_MID_BOTTOM  # 创建好玩家飞机后，设置玩家飞机位置
        pygame.time.set_timer(HERO_FIRE_EVENT, 300)  # 创建玩家飞机之后0.3秒启动一次发射子弹事件



    def update(self, *args):
        '''args 的0号下标说明是否要更新下一帧动画
                  1号下标是水平方向移动基数
                  1号下标是垂直方向移动基数
        '''
        super(Hero, self).update(*args)

        if len(args) != 3 or self.hp <= 0:
            return

        # 屏幕边缘的位置修正
        self.rect.x += args[1] * self.speed
        self.rect.x = 0 if self.rect.x < 0 else self.rect.x
        if self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right

        self.rect.y += args[2] * self.speed
        self.rect.y = 0 if self.rect.y < 0 else self.rect.y
        if self.rect.bottom > SCREEN_RECT.bottom:
            self.rect.bottom = SCREEN_RECT.bottom

    def blowup(self, enemies_group):
        '''炸毁所有敌机,返回得到的总分'''
        # 判断是否能够发起引爆
        if self.bomb_count <= 0 or self.hp <= 0:
            return 0

        # 引爆所有敌机并且累计得分
        self.bomb_count -= 1

        score = 0
        count = 0
        for enemy in enemies_group.sprites():
            if enemy.rect.bottom > 0:
                score += enemy.value
                enemy.hp = 0
                count += 1

        return score

    def reset_plan(self):
        super(Hero, self).reset_plan()

        self.is_power = True  # 撞击之后无敌设置
        self.bomb_count = HERO_BOMB_COUNT
        self.bullets_kind = 0

        # 发布事件，让游戏主逻辑更新界面
        pygame.event.post(pygame.event.Event(HERO_DEAD_EVENT))

        # 发布定时事件
        pygame.time.set_timer(HERO_POWER_OFF_EVENT, 3000)  # 3秒钟无敌

    def fire(self, display_group):
        '''玩家飞机发射新一轮的子弹'''
        # 准备子弹要显示到的组
        groups = (display_group, self.bullets_group)

        # 创建新的子弹类
        for i in range(3):
            bullet1 = Bullet(self.bullets_kind, *groups)
            y = self.rect.y - i*30
            if self.bullets_kind == 0:
                bullet1.rect.midbottom = (self.rect.centerx, y)
            else:
                bullet1.rect.midbottom = (self.rect.centerx - 30, y + 60)
                bullet2 = Bullet(self.bullets_kind, *groups)
                bullet2.rect.midbottom = (self.rect.centerx + 30, y + 60)



class Bullet(GameSprite):
    '''子弹类'''
    def __init__(self, kind, *group):
        '''初始化子弹数据'''
        image_name ='bullet1.png' if kind == 0 else 'bullet2.png'
        super(Bullet, self).__init__(image_name, -15, *group)
        self.damage = 1  # 杀伤力

    def update(self, *args):
        '''更新子弹的数据'''
        super(Bullet, self).update(*args)

        # 检测飞出屏幕之外则销毁子弹
        if self.rect.bottom < 0:
            self.kill()


class Supply(GameSprite):
    '''道具精灵'''
    def __init__(self, kind, *group):
        '''初始化道具属性'''
        image_name = 'bomb_supply.png' if kind == 0 else 'bullet_supply.png'
        super(Supply, self).__init__(image_name, 3, *group)

        self.kind = kind  # 道具类型
        self.wav_name = 'boom.wav' if kind == 0 else 'boom.wav'  # 道具的音效

        self.rect.bottom = SCREEN_RECT.h  # 道具初始位置

    def update(self, *args):
        '''修改道具位置'''
        if self.rect.y > SCREEN_RECT.h:  # 如果已经移动到屏幕之外则不需要更新位置
            return

        super(Supply, self).update(*args)

    def throw_supply(self):
        '''投放道具'''
        self.rect.bottom = 0  # 移动道具到窗口底部
        self.rect.x = random.randint(0, SCREEN_RECT.w - self.rect.w)

