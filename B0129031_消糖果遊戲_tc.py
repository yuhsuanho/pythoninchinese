﻿#---原版作者---
'''
Gemgem (a Bejeweled clone)
By Al Sweigart al@inventwithpython.com
http://inventwithpython.com/pygame
Released under a "Simplified BSD" license
'''
#--改版作者---
"""
遊戲名稱:消糖果遊戲
學號:b0129031
"""

import random, time, pygame, sys, copy
from pygame.locals import *
from pygame_tc import *

#from zipfile import *
'''
    #讀取壓縮檔名稱
    z=ZipFile('picture.zip','r')    
    圖檔 =[]
    圖檔名 =[]
    for f in z.namelist():
        圖檔名+=[f]
        圖檔+=z.read(f)
'''

畫面更新率 = 30 #FPS
視窗寬度 = 600  # 程式視窗寬度(單位為像素)
視窗高度 = 600 

版面總欄位數 = 8 
版面總列數 = 8 
糖果圖片大小 = 64 # 每個空間的高度和寬度(單位為像素)

糖果圖片總數 = 7
assert 糖果圖片總數 >= 5 # 遊戲需要至少五種以上的糖果才能運作

配對成功的音效總數 = 6

移動速率 = 25 #範圍是1~100 , 數字越大移動越快
扣除速度 = 1 # 分數是以每秒的速度遞減2分

#三原色光模式 R    G    B
紫色      = (255,   0, 255)
愛麗絲藍  = (130, 206, 250)
皇藍色    = ( 30, 144, 255)
黃色      = (255, 255,   0)
黑色      = (  0,   0,   0)
紅色      = (255,   0,   0)
選取邊的顏色 = 紫色 
視窗背景顏色 = 愛麗絲藍 
版面顏色 = 皇藍色 
遊戲結束字體顏色 = 黃色 
遊戲結束背景顏色 = 黑色 
分數的顏色 = 紅色 

X軸剩餘邊界 = int((視窗寬度 - 糖果圖片大小 * 版面總欄位數) / 2)
Y軸剩餘邊界 = int((視窗高度 - 糖果圖片大小 * 版面總列數) / 2)

# 表示方向的定量
上 = 'up'
下 = 'down'
左 = 'left'
右 = 'right'

空的空間 = -1 # 一個任意非正數來判斷空的空間
面板上方的列 = 'row above 面版' # 一個任意非整數的值

def 主函式():
    global 畫面更新時鐘, 版面展示, 糖果圖片, 糖果音效, 預設字體, 矩形版面

    # 初始化設置
    遊戲開始()
    畫面更新時鐘 = 時鐘物件()
    版面展示 = 設螢幕大小((視窗寬度, 視窗高度))
    設螢幕標題('消糖果遊戲') 
    預設字體 = 字型物件('freesansbold.ttf', 36)

    # 載入圖片
    糖果圖片 = []
    for i in 範圍(1, 糖果圖片總數+1):
        圖片 = 圖片載入('candy%s.png' % i)
        if 圖片.get_size() != (糖果圖片大小, 糖果圖片大小):
            圖片 = 轉換任意平滑版面(圖片, (糖果圖片大小, 糖果圖片大小))
        糖果圖片.append(圖片)

    # 載入音效
    糖果音效 = {}
    糖果音效['bad swap'] = 聲音物件('badswap.wav')
    糖果音效['match'] = []
    for i in 範圍(配對成功的音效總數):
        糖果音效['match'].append(聲音物件('match%s.wav' % i))
        
    # 為每個面板空間創造矩形物件，並做面板座標到像素座標的轉換
    矩形版面 = []
    for x in 範圍(版面總欄位數):
        矩形版面.append([])
        for y in 範圍(版面總列數):
            r = 矩形物件((X軸剩餘邊界 + (x * 糖果圖片大小),
                             Y軸剩餘邊界 + (y * 糖果圖片大小),
                             糖果圖片大小,
                             糖果圖片大小))
            矩形版面[x].append(r)

    while True:
        開始遊戲()

def 開始遊戲():
    # Plays through a single game. When the game is over, this function returns.

    # 初始化面版
    遊戲面板 = 取得空白面板()
    得分 = 0
    填面板並產生動畫(遊戲面板, [], 得分) 

    # 開始新遊戲時,初始化變數
    第一個選取的糖果 = None
    最後滑鼠往下的x軸 = None
    最後滑鼠往下的y軸 = None
    遊戲是否結束 = False
    最後扣除分數 = 時間()
    單擊繼續字體版面= None

    while True: # 主遊戲迴圈
        被點擊空間 = None
        for 事件 in 事件取得(): # 處理事件的迴圈
            if 事件.type == QUIT or (事件.type == KEYUP and 事件.key == K_ESCAPE):
                遊戲結束()
                系統離開()
            elif 事件.type == KEYUP and 事件.key == K_BACKSPACE:
                return # 開始新遊戲

            elif 事件.type == MOUSEBUTTONUP:
                if 遊戲是否結束:
                    return # 遊戲結束後,點擊開始新遊戲

                if 事件.pos == (最後滑鼠往下的x軸, 最後滑鼠往下的y軸):
                    # This event is a mouse click, not the end of a mouse drag.
                    被點擊空間 = 糖果是否點擊在正確位置(事件.pos)
                else:
                    # this is the end of a mouse drag
                    第一個選取的糖果 = 糖果是否點擊在正確位置((最後滑鼠往下的x軸, 最後滑鼠往下的y軸))
                    被點擊空間 = 糖果是否點擊在正確位置(事件.pos)
                    if not 第一個選取的糖果 or not 被點擊空間:
                        # if not part of a valid drag, deselect both
                        第一個選取的糖果 = None
                        被點擊空間 = None
            elif 事件.type == MOUSEBUTTONDOWN:
                # this is the start of a mouse click or mouse drag
                最後滑鼠往下的x軸, 最後滑鼠往下的y軸 = 事件.pos

        if 被點擊空間 and not 第一個選取的糖果:
            # This was the first gem clicked on.
            第一個選取的糖果 = 被點擊空間
        elif 被點擊空間 and 第一個選取的糖果:
            # Two gems have been clicked on and selected. Swap the gems.
            交換中第一個糖果, 交換中第二個糖果 = 取得交換的糖果(遊戲面板, 第一個選取的糖果, 被點擊空間)
            if 交換中第一個糖果 == None and 交換中第二個糖果 == None:
                # If both are None, then the gems were not adjacent
                第一個選取的糖果 = None # deselect the first gem
                continue

            # Show the swap animation on the screen.
            面板複製 = 取得複製消除糖果的面板(遊戲面板, (交換中第一個糖果, 交換中第二個糖果))
            產生移動中的糖果們(面板複製, [交換中第一個糖果, 交換中第二個糖果], [], 得分)

            # Swap the gems in the board data structure.
            遊戲面板[交換中第一個糖果['x']][交換中第一個糖果['y']] = 交換中第二個糖果['imageNum']
            遊戲面板[交換中第二個糖果['x']][交換中第二個糖果['y']] = 交換中第一個糖果['imageNum']

            # See if this is a matching move.
            相同糖果組 = 尋找匹配的糖果(遊戲面板)
            if 相同糖果組 == []:
                # Was not a matching move; swap the gems back
                糖果音效['bad swap'].play()
                產生移動中的糖果們(面板複製, [交換中第一個糖果, 交換中第二個糖果], [], 得分)
                遊戲面板[交換中第一個糖果['x']][交換中第一個糖果['y']] = 交換中第一個糖果['imageNum']
                遊戲面板[交換中第二個糖果['x']][交換中第二個糖果['y']] = 交換中第二個糖果['imageNum']
            else:
                # This was a matching move.
                增加分數 = 0
                while 相同糖果組 != []:
                    # Remove matched gems, then pull down the board.

                    # points is a list of dicts that tells fillBoardAndAnimate()
                    # where on the screen to display text to show how many
                    # points the player got. points is a list because if
                    # the playergets multiple matches, then multiple points text should appear.

                    分數陣列 = []
                    for 糖果集合 in 相同糖果組:
                        增加分數 += (10 + (len(糖果集合) - 3) * 10)
                        for 糖果 in 糖果集合:
                            遊戲面板[糖果[0]][糖果[1]] = 空的空間
                        分數陣列.append({'分數陣列': 增加分數,
                                       'x': 糖果[0] * 糖果圖片大小 + X軸剩餘邊界,
                                       'y': 糖果[1] * 糖果圖片大小 + Y軸剩餘邊界})
                    隨機選擇(糖果音效['match']).play()
                    得分 += 增加分數

                    # Drop the new gems.
                    填面板並產生動畫(遊戲面板, 分數陣列, 得分)

                    # Check if there are any new matches.
                    相同糖果組 = 尋找匹配的糖果(遊戲面板)
            第一個選取的糖果 = None

            if not 可做出移動(遊戲面板):
                遊戲是否結束 = True

        # Draw the board.
        版面展示.fill(視窗背景顏色)
        畫面板(遊戲面板)
        if 第一個選取的糖果 != None:
            凸顯選取空間(第一個選取的糖果['x'], 第一個選取的糖果['y'])
        if 遊戲是否結束:
            if 單擊繼續字體版面 == None:
                # Only render the text once. In future iterations, just
                # use the Surface object already in clickContinueTextSurf
                單擊繼續字體版面 = 預設字體.render('Final Score: %s (Click to continue)' % (得分), 1, 遊戲結束字體顏色, 遊戲結束背景顏色)
                單擊繼續字體矩形區 = 單擊繼續字體版面.get_rect()
                單擊繼續字體矩形區.center = int(視窗寬度 / 2), int(視窗高度 / 2)
            版面展示.blit(單擊繼續字體版面, 單擊繼續字體矩形區)
        elif 得分 > 0 and 時間() - 最後扣除分數 > 扣除速度:
            # 得分 drops over time
            得分 -= 2
            最後扣除分數 = 時間()
        繪製分數(得分)
        顯示幕更新()
        畫面更新時鐘.tick(畫面更新率)


def 取得交換的糖果(面版, 第一個座標, 第二個座標):
    # If the gems at the (X, Y) coordinates of the two gems are adjacent,
    # then their 'direction' keys are set to the appropriate direction
    # value to be swapped with each other.
    # Otherwise, (None, None) is returned.
    第一個糖果 = {'imageNum': 面版[第一個座標['x']][第一個座標['y']],
                'x': 第一個座標['x'],
                'y': 第一個座標['y']}
    第二個糖果 = {'imageNum': 面版[第二個座標['x']][第二個座標['y']],
                 'x': 第二個座標['x'],
                 'y': 第二個座標['y']}
    標示糖果 = None
    if 第一個糖果['x'] == 第二個糖果['x'] + 1 and 第一個糖果['y'] == 第二個糖果['y']:
        第一個糖果['direction'] = 左
        第二個糖果['direction'] = 右
    elif 第一個糖果['x'] == 第二個糖果['x'] - 1 and 第一個糖果['y'] == 第二個糖果['y']:
        第一個糖果['direction'] = 右
        第二個糖果['direction'] = 左
    elif 第一個糖果['y'] == 第二個糖果['y'] + 1 and 第一個糖果['x'] == 第二個糖果['x']:
        第一個糖果['direction'] = 上
        第二個糖果['direction'] = 下
    elif 第一個糖果['y'] == 第二個糖果['y'] - 1 and 第一個糖果['x'] == 第二個糖果['x']:
        第一個糖果['direction'] = 下
        第二個糖果['direction'] = 上
    else:
        # These gems are not adjacent and can't be swapped.
        return None, None
    return 第一個糖果, 第二個糖果

def 取得空白面板():
    # Create and return a blank board data structure.
    面版 = []
    for x in 範圍(版面總欄位數):
        面版.append([空的空間] * 版面總列數)
    return 面版

def 可做出移動(面版):
    # Return True if the board is in a state where a matching
    # move can be made on it. Otherwise return False.

    # The patterns in oneOffPatterns represent gems that are configured
    # in a way where it only takes one move to make a triplet.
    統一模式 = (((0,1), (1,0), (2,0)),
                      ((0,1), (1,1), (2,0)),
                      ((0,0), (1,1), (2,0)),
                      ((0,1), (1,0), (2,1)),
                      ((0,0), (1,0), (2,1)),
                      ((0,0), (1,1), (2,1)),
                      ((0,0), (0,2), (0,3)),
                      ((0,0), (0,1), (0,3)))
    # The x and y variables iterate over each space on the board.
    # If we use + to represent the currently iterated space on the
    # board, then this pattern: ((0,1), (1,0), (2,0))refers to identical
    # gems being set up like this:
    #
    #     +A
    #     B
    #     C
    #
    # That is, gem A is offset from the + by (0,1), gem B is offset
    # by (1,0), and gem C is offset by (2,0). In this case, gem A can
    # be swapped to the left to form a vertical three-in-a-row triplet.
    #
    # There are eight possible ways for the gems to be one move
    # away from forming a triple, hence oneOffPattern has 8 patterns.
    for x in 範圍(版面總欄位數):
        for y in 範圍(版面總列數):
            for pat in 統一模式:
                # check each possible pattern of "match in next move" to
                # see if a possible move can be made.
                if (取得糖果位置(面版, x+pat[0][0], y+pat[0][1]) == \
                    取得糖果位置(面版, x+pat[1][0], y+pat[1][1]) == \
                    取得糖果位置(面版, x+pat[2][0], y+pat[2][1]) != None) or \
                   (取得糖果位置(面版, x+pat[0][1], y+pat[0][0]) == \
                    取得糖果位置(面版, x+pat[1][1], y+pat[1][0]) == \
                    取得糖果位置(面版, x+pat[2][1], y+pat[2][0]) != None):
                    return True # return True the first time you find a pattern
    return False

def 畫出移動中的糖果(糖果, 過程):
    # Draw a gem sliding in the direction that its 'direction' key
    # indicates. The progress parameter is a number from 0 (just
    # starting) to 100 (slide complete).
    移動x = 0
    移動y = 0
    過程 *= 0.01

    if 糖果['direction'] == 上:
        移動y = -int(過程 * 糖果圖片大小)
    elif 糖果['direction'] == 下:
        移動y = int(過程 * 糖果圖片大小)
    elif 糖果['direction'] == 右:
        移動x = int(過程 * 糖果圖片大小)
    elif 糖果['direction'] == 左:
        移動x = -int(過程 * 糖果圖片大小)

    原本的x座標 = 糖果['x']
    原本的y座標 = 糖果['y']
    if 原本的y座標 == 面板上方的列:
        原本的y座標 = -1

    x座標的像素 = X軸剩餘邊界 + (原本的x座標 * 糖果圖片大小)
    y座標的像素 = Y軸剩餘邊界 + (原本的y座標 * 糖果圖片大小)
    r = 矩形物件( (x座標的像素 + 移動x, y座標的像素 + 移動y, 糖果圖片大小, 糖果圖片大小) )
    版面展示.blit(糖果圖片[糖果['imageNum']], r)

def 拉下全部糖果(面版):
    # pulls down gems on the board to the bottom to fill in any gaps
    for x in 範圍(版面總欄位數):
        欄位中的糖果 = []
        for y in 範圍(版面總列數):
            if 面版[x][y] != 空的空間:
                欄位中的糖果.append(面版[x][y])
        面版[x] = ([空的空間] * (版面總列數 - len(欄位中的糖果))) + 欄位中的糖果

def 取得糖果位置(面版, x, y):
    if x < 0 or y < 0 or x >= 版面總欄位數 or y >= 版面總列數:
        return None
    else:
        return 面版[x][y]

def 取得下拉槽(面版):
    # Creates a "drop slot" for each column and fills the slot with a
    # number of gems that that column is lacking. This function assumes
    # that the gems have been gravity dropped already.
    面板複製 = 深層複製(面版)
    拉下全部糖果(面板複製)

    掉落位置 = []
    for i in 範圍(版面總欄位數):
        掉落位置.append([])

    # count the number of empty spaces in each column on the 面版
    for x in 範圍(版面總欄位數):
        for y in 範圍(版面總列數-1, -1, -1): # start from bottom, going up
            if 面板複製[x][y] == 空的空間:
                有可能性的糖果 = list(範圍(len(糖果圖片)))
                for x軸相抵量, y軸相抵量 in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                    # Narrow down the possible 糖果們 we should put in the
                    # blank space so we don't end up putting an two of
                    # the same 糖果們 next to each other when they drop.
                    糖果的鄰居 = 取得糖果位置(面板複製, x + x軸相抵量, y + y軸相抵量)
                    if 糖果的鄰居 != None and 糖果的鄰居 in 有可能性的糖果:
                        有可能性的糖果.remove(糖果的鄰居)

                新糖果 = 隨機選擇(有可能性的糖果)
                面板複製[x][y] = 新糖果
                掉落位置[x].append(新糖果)
    return 掉落位置

def 尋找匹配的糖果(面版):
    要移除的糖果 = [] # a list of lists of 糖果們 in matching triplets that should be removed
    面板複製 = 深層複製(面版)

    # loop through each space, checking for 3 adjacent identical 糖果們
    for x in 範圍(版面總欄位數):
        for y in 範圍(版面總列數):
            # look for horizontal matches
            if 取得糖果位置(面板複製, x, y) == 取得糖果位置(面板複製, x + 1, y) == 取得糖果位置(面板複製, x + 2, y) and 取得糖果位置(面板複製, x, y) != 空的空間:
                目標糖果 = 面板複製[x][y]
                相抵量 = 0
                移除的集合 = []
                while 取得糖果位置(面板複製, x + 相抵量, y) == 目標糖果:
                    # keep checking if there's more than 3 糖果們 in a row
                    移除的集合.append((x + 相抵量, y))
                    面板複製[x + 相抵量][y] = 空的空間
                    相抵量 += 1
                要移除的糖果.append(移除的集合)

            # look for vertical matches
            if 取得糖果位置(面板複製, x, y) == 取得糖果位置(面板複製, x, y + 1) == 取得糖果位置(面板複製, x, y + 2) and 取得糖果位置(面板複製, x, y) != 空的空間:
                目標糖果 = 面板複製[x][y]
                相抵量 = 0
                移除的集合 = []
                while 取得糖果位置(面板複製, x, y + 相抵量) == 目標糖果:
                    # keep checking, in case there's more than 3 糖果們 in a row
                    移除的集合.append((x, y + 相抵量))
                    面板複製[x][y + 相抵量] = 空的空間
                    相抵量 += 1
                要移除的糖果.append(移除的集合)

    return 要移除的糖果

def 凸顯選取空間(x, y):
    畫矩形(版面展示, 選取邊的顏色, 矩形版面[x][y], 4)

def 取得掉落中的糖果(面版):
    # Find all the 糖果們 that have an empty space below them
    面板複製 = 深層複製(面版)
    掉落中的糖果 = []
    for x in 範圍(版面總欄位數):
        for y in 範圍(版面總列數 - 2, -1, -1):
            if 面板複製[x][y + 1] == 空的空間 and 面板複製[x][y] != 空的空間:
                # This space drops if not empty but the space below it is
                掉落中的糖果.append( {'imageNum': 面板複製[x][y], 'x': x, 'y': y, 'direction': 下} )
                面板複製[x][y] = 空的空間
    return 掉落中的糖果

def 產生移動中的糖果們(面版, 糖果們, 分數們的文字, 得分):
    # 分數們的文字 is a dictionary with keys 'x', 'y', and '分數陣列'
    過程 = 0 # 過程 at 0 represents beginning, 100 means finished.
    while 過程 < 100: # animation loop
        版面展示.fill(視窗背景顏色)
        畫面板(面版)
        for 糖果 in 糖果們: # Draw each 糖果.
            畫出移動中的糖果(糖果, 過程)
        繪製分數(得分)
        for 分數文字 in 分數們的文字:
            分數面板 = 預設字體.render(str(分數文字['分數陣列']), 1, 分數的顏色)
            分數的矩形 = 分數面板.get_rect()
            分數的矩形.center = (分數文字['x'], 分數文字['y'])
            版面展示.blit(分數面板, 分數的矩形)

        顯示幕更新()
        畫面更新時鐘.tick(畫面更新率)
        過程 += 移動速率 # 過程 the animation a little bit more for the next frame

def 移動糖果們(面版, 移動中的糖果):
    for 糖果 in 移動中的糖果:
        if 糖果['y'] != 面板上方的列:
            面版[糖果['x']][糖果['y']] = 空的空間
            移動x = 0
            移動y = 0
            if 糖果['direction'] == 左:
                移動x = -1
            elif 糖果['direction'] == 右:
                移動x = 1
            elif 糖果['direction'] == 下:
                移動y = 1
            elif 糖果['direction'] == 上:
                移動y = -1
            面版[糖果['x'] + 移動x][糖果['y'] + 移動y] = 糖果['imageNum']
        else:
            # 糖果 is located above the 面版 (where new 糖果們 come from)
            面版[糖果['x']][0] = 糖果['imageNum'] # move to top row

def 填面板並產生動畫(面版, 分數陣列, 得分):
    掉落位置 = 取得下拉槽(面版)
    while 掉落位置 != [[]] * 版面總欄位數:
        # do the dropping animation as long as there are more 糖果們 to drop
        移動中的糖果 = 取得掉落中的糖果(面版)
        for x in 範圍(len(掉落位置)):
            if len(掉落位置[x]) != 0:
                # cause the lowest 糖果 in each slot to begin moving in the 下 direction
                移動中的糖果.append({'imageNum': 掉落位置[x][0], 'x': x, 'y': 面板上方的列, 'direction': 下})

        面板複製 = 取得複製消除糖果的面板(面版, 移動中的糖果)
        產生移動中的糖果們(面板複製, 移動中的糖果, 分數陣列, 得分)
        移動糖果們(面版, 移動中的糖果)

        # Make the next row of 糖果們 from the drop slots
        # the lowest by deleting the previous lowest 糖果們.
        for x in 範圍(len(掉落位置)):
            if len(掉落位置[x]) == 0:
                continue
            面版[x][0] = 掉落位置[x][0]
            del 掉落位置[x][0]

def 糖果是否點擊在正確位置(位置):
    # See if the mouse click was on the 面版
    for x in 範圍(版面總欄位數):
        for y in 範圍(版面總列數):
            if 矩形版面[x][y].collidepoint(位置[0], 位置[1]):
                return {'x': x, 'y': y}
    return None # Click was not on the 面版.

def 畫面板(面版):
    for x in 範圍(版面總欄位數):
        for y in 範圍(版面總列數):
            畫矩形(版面展示, 版面顏色, 矩形版面[x][y], 1)
            畫糖果的空間 = 面版[x][y]
            if 畫糖果的空間 != 空的空間:
                版面展示.blit(糖果圖片[畫糖果的空間], 矩形版面[x][y])

def 取得複製消除糖果的面板(面版, 糖果們):
    # Creates and returns a copy of the passed 面版 data structure,
    # with the 糖果們 in the "糖果們" list removed from it.
    #
    # Gems is a list of dicts, with keys x, y, direction, imageNum

    面板複製 = 深層複製(面版)

    # Remove some of the 糖果們 from this 面版 data structure copy.
    for 糖果 in 糖果們:
        if 糖果['y'] != 面板上方的列:
            面板複製[糖果['x']][糖果['y']] = 空的空間
    return 面板複製

def 繪製分數(得分):
    分數圖片 = 預設字體.render(str(得分), 1, 分數的顏色)
    分數主題 = 分數圖片.get_rect()
    分數主題.bottomleft = (10, 視窗高度 - 6)
    版面展示.blit(分數圖片, 分數主題)

if __name__ == '__main__':
    主函式()
