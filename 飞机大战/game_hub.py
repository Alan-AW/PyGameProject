'''
控制面板/提示信息
'''

import pygame
pygame.init()
from game_items import *

class HUDPanel(object):
    '''所有面板精灵的控制类'''

    margin = 10  # 精灵之间的间距
    white = (255, 255, 255)  # 白色
    gray = (64, 64, 64)  # 灰色
    reward_score = 400000  # 奖励分值
    level2_score = 50000  # 级别2分值
    level3_score = 150000  # 级别3分值
    record_failename = 'record.txt'  # 最好成绩文件名

    def __init__(self, display_group):
        # 基本数据
        self.score = 0  # 游戏得分
        self.lives_count = 3  # 初始生命值
        self.level = 1  # 游戏级别
        self.best_score = 0  #最好成绩

        # 图像精灵
        # 状态按钮
        self.status_sprite = StatusButton(('pause_nor.png', 'resume_nor.png') ,display_group)
        self.status_sprite.rect.topleft = (self.margin, self.margin)

        # 炸弹精灵
        self.bomb_sprite = GameSprite('bomb_supply.png', 0, display_group)
        self.bomb_sprite.rect.bottomleft = (self.margin, SCREEN_RECT.bottom - self.margin)

        # 炸弹计数标签
        self.bomb_label = Label('X 3', 32, self.gray, display_group)
        self.bomb_label.rect.midleft = (self.bomb_sprite.rect.right + self.margin,
                                         self.bomb_sprite.rect.centery)

        # 生命计数标签
        self.lives_label = Label('X %d' % self.lives_count, 32, self.gray, display_group)
        self.lives_label.rect.midright = (SCREEN_RECT.right - self.margin,
                                          self.bomb_label.rect.centery)

        # 调整生命精灵位置
        self.lives_sprite = GameSprite('life.png', 0, display_group)
        self.lives_sprite.rect.right = self.lives_label.rect.left - self.margin
        self.lives_sprite.rect.bottom = SCREEN_RECT.bottom - (self.margin * 2)

        # 得分标签
        self.score_label = Label('%d' %self.score, 32, self.gray, display_group)
        self.score_label.rect.midleft = (self.status_sprite.rect.right + self.margin,
                                         self.status_sprite.rect.centery)

        # 最好成绩标签
        self.best_label = Label('Best:%d' % self.best_score, 36, self.white)
        self.best_label.rect.center = SCREEN_RECT.center

        # 状态标签
        self.status_label = Label('Game Paused', 48, self.white)
        self.status_label.rect.midbottom = (self.best_label.rect.centerx,
                                            self.best_label.rect.y - 2*self.margin)


        # 提示标签
        self.tip_label = Label('Press spacebar to continue', 22, self.white)
        self.tip_label.rect.midtop = (self.best_label.rect.centerx,
                                      self.best_label.rect.bottom + 8*self.margin)

        # 从文件里面加载最好成绩
        self.load_best_score()
        print('初始化控制面板当前最好得分是：', self.best_score)

    def show_bomb(self, count):
        '''
        修改炸弹数量为X lives_count
        '''
        self.bomb_label.set_text('X %d' %count)
        self.bomb_label.rect.midleft = (self.bomb_sprite.rect.right + self.margin,
                                        self.bomb_sprite.rect.centery)

    def show_lives(self):
        '''显示最新的生命计数'''
        self.lives_label.set_text('X %d' %self.lives_count)

        # 修改生命计数位置
        self.lives_label.rect.midright = (SCREEN_RECT.right - self.margin,
                                          self.bomb_label.rect.centery)

        # 调整生命精灵位置  同一个飞机修改右边位置，所以不需要修改底部位置
        self.lives_sprite.rect.right = self.lives_label.rect.left - self.margin

    def increase_score(self, enemy_score):
        '''增加得分，注意同时处理增加生命，关卡升级，跟新最好成绩'''

        # 计算最新得分
        score = self.score + enemy_score

        # 判断是否增加生命
        if score // self.reward_score != self.score // self.reward_score:
            self.lives_count += 1
            self.show_lives()

        self.score = score

        # 跟新最好成绩
        self.best_score = score if score > self.best_score else self.best_score

        # 计算最新关卡等级
        if score < self.level2_score:
            level = 1
        elif score < self.level3_score:
            level = 2
        else:level = 3

        is_upgrade = level != self.level
        self.level = level

        # 跟新得分精灵显示内容和位置
        self.score_label.set_text('%d' %score)
        self.score_label.rect.midleft = (self.status_sprite.rect.right + self.margin,
                                         self.status_sprite.rect.centery)

        # 返回是否升级给游戏主逻辑
        return is_upgrade
    def save_best_score(self):
        '''保存当前最好得分到文件下'''
        fail = open(self.record_failename, 'w')
        fail.write(str(self.best_score))
        fail.close()

    def load_best_score(self):
        '''从文件里面重新加载最好得分'''
        try:
        # 读取文件内容
            fail = open(self.record_failename, 'r')
            content = fail.read()
            fail.close()
        # 转换内容为数字，赋值给最好成绩
            self.best_score = int(content)
        except (FileNotFoundError, ValueError):
            print('读取最高得分文件发生异常...')

    def panel_paused(self, is_game_over, displays_group):
        '''停止游戏，显示提示信息'''
        # 判断是否已经显示内容了
        if displays_group.has(self.best_label,
                              self.status_label,
                              self.tip_label):
            return

        # 根据是否游戏结束决定显示要显示的文字
        status = 'G G!' if is_game_over else 'Go on!'
        tip = 'Push Space to '
        tip += 'Again' if is_game_over else 'Continue'

        # 修改标签精灵的文本内容
        self.best_label.set_text('Your beat Score:%d' %self.best_score)
        self.status_label.set_text(status)
        self.tip_label.set_text(tip)

        # 修正标签精灵的位置
        self.best_label.rect.center = SCREEN_RECT.center

        self.status_label.rect.midbottom = (self.best_label.rect.centerx,
                                            self.best_label.rect.y - 2 * self.margin)

        self.tip_label.rect.midtop = (self.best_label.rect.centerx,
                                      self.best_label.rect.bottom + 5 * self.margin)

        # 把标签精灵添加到精灵组
        displays_group.add(self.best_label, self.status_label, self.tip_label)

        # 修改状态按钮
        self.status_sprite.swicth_status(True)

    def panel_resum(self, display_group):
        '''取消停止状态，隐藏提示信息'''
        display_group.remove(self.best_label, self.status_label, self.tip_label)

        self.status_sprite.swicth_status(False)

    def reset_panel(self):
        '''重置面板数据'''
        # 重置数据
        self.score = 0
        self.lives_count = 3

        # 重置精灵数据
        self.increase_score(0)
        self.show_bomb(3)
        self.show_lives()
