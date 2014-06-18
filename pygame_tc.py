'''
將此遊戲內用到的英文函式，建立中文名稱
pygame模組常用函式庫和大部分常用的函式
'''

import random,time,pygame,sys,copy
from pygame.locals import *
from pygame import Surface

#下列是將函式從英文名稱擴充為中文名稱
範圍 = range
印 = print
遊戲開始 = pygame.init
遊戲結束 = pygame.quit

時鐘物件 = pygame.time.Clock
程式等待時間 = pygame.time.wait

設螢幕大小 = pygame.display.set_mode
設螢幕標題= pygame.display.set_caption
顯示幕更新 = pygame.display.update

字型物件 = pygame.font.Font
圖片載入 = pygame.image.load
時間 = time.time
轉換任意平滑版面 = pygame.transform.smoothscale

聲音物件 =  pygame.mixer.Sound


事件取得 = pygame.event.get
事件張貼 = pygame.event.post

系統離開 = sys.exit
隨機選擇 = random.choice
深層複製 = copy.deepcopy

畫矩形 = pygame.draw.rect
矩形物件 = pygame.Rect

