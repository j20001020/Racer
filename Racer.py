import pygame
import sys
import math
import random
from  pygame.locals import  *

# 定義顏色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW= (255, 224, 0)
GREEN = (0, 255, 0)

# 定義參數
index = 0
counter = 0
laps = 0
record = 0
record_temp = 0
sound_crash = None
mycar = 0

# 賽道設計
DATA_LR = [0, 0, 0, 1, 2, 4,  1,  0, -3,-1, 0, 0] # 賽道彎曲設計
DATA_UD = [0, 0, 1, 2, 3, 2,  1,  0, -2,-4,-2, 0] # 賽道坡設計
# DATA_LR = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 2, 1, 0, 2, 4, 2, 4, 2, 0, 0, 0,-2,-2,-4,-4,-2,-1, 0, 0, 0, 0, 0, 0, 0] # 賽道彎曲設計
# DATA_UD = [0, 0, 1, 2, 3, 2, 1, 0,-2,-4,-2, 0, 0, 0, 0, 0,-1,-2,-3,-4,-3,-2,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 3, 0,-6, 6, 0] # 賽道坡設計
CLEN = len(DATA_LR)

Board = 120
CMax = Board*CLEN
curve = [0]*CMax
updown = [0]*CMax
object_left = [0]*CMax
object_right = [0]*CMax

CAR = 10
car_x = [0]*CAR
car_y = [0]*CAR
car_lr = [0]*CAR
car_spd = [0]*CAR
PLAYER_CAR_Y = 10   # 玩家賽車的顯示位置

GAME_LAPS = 3
laptime = ["0'00.00"]*GAME_LAPS

def make_course():
    for i in range(CLEN):
        lr1 = DATA_LR[i]
        lr2 = DATA_LR[(i+1)%CLEN]
        ud1 = DATA_UD[i]
        ud2 = DATA_UD[(i+1)%CLEN]
        for j in range(Board):
            pos = j+Board*i
            curve[pos] = lr1*(Board-j)/Board + lr2*j/Board
            updown[pos] = ud1*(Board-j)/Board + ud2*j/Board
            if j == 60:
                object_right[pos] = 1 # 看板
            if i%8 < 7:
                if j%12 == 0:
                    object_left[pos] = 2 # 椰子樹
            else:
                if j%20 == 0:
                    object_left[pos] = 3 # 遊艇
            if j%12 == 6:
                object_left[pos] = 9 # 海


def time_str(val):
    sec = int(val)  # 參數變成整數的秒數
    ms = int((val-sec)*100) # 毫秒
    min = int(sec/60)  # 分鐘
    return "{}'{:02}.{:02}".format(min, sec%60, ms)


def draw_obj(bg, img, x, y, sc):
    img_rz = pygame.transform.rotozoom(img, 0, sc)
    w = img_rz.get_width()
    h = img_rz.get_height()
    bg.blit(img_rz, [x-w/2, y-h])


def draw_shadow(bg, x, y, siz):
    shadow = pygame.Surface([siz, siz/4])
    shadow.fill(RED)
    shadow.set_colorkey(RED) # 設定Surface的透明色
    shadow.set_alpha(128) # 設定Surface的透明度
    pygame.draw.ellipse(shadow, BLACK, [0,0,siz,siz/4])
    bg.blit(shadow, [x-siz/2, y-siz/4])


# 賽車初始化
def init_car():
    for i in range(1, CAR):
        car_x[i] = random.randint(50, 750)
        car_y[i] = random.randint(200, CMax-200)
        car_lr[i] = 0
        car_spd[i] = random.randint(100, 200)
    car_x[0] = 400
    car_y[0] = 0
    car_lr[0] = 0
    car_spd[0] = 0


# 控制玩家的賽車
def drive_car(key):
    global  index, counter, laps, record_temp
    if key[K_LEFT] == 1:
        if car_lr[0] > -3:
            car_lr[0] -= 1
        car_x[0] = car_x[0] + (car_lr[0]-3)*car_spd[0]/100 - 5
    elif key[K_RIGHT] == 1:
        if car_lr[0] < 3:
            car_lr[0] += 1
        car_x[0] = car_x[0] + (car_lr[0]+3)*car_spd[0]/100 + 5
    else:
        car_lr[0] = int(car_lr[0]*0.9)

    if key[K_UP] == 1:  # 油門
        car_spd[0] += 3
    elif key[K_DOWN] == 1: # 煞車
        car_spd[0] -= 10
    else:
        car_spd[0] -= 0.25

    if car_spd[0] < 0:
        car_spd[0] = 0
    if car_spd[0] > 320: # 最高時速
        car_spd[0] = 320

    car_x[0] -= car_spd[0]*curve[int(car_y[0]+PLAYER_CAR_Y)%CMax]/50
    if car_x[0] < 0:
        car_x[0] = 0
        car_spd[0] *= 0.9
    if car_x[0] > 800:
        car_x[0] = 800
        car_spd[0] *= 0.9

    car_y[0] = car_y[0] + car_spd[0]/100
    if car_y[0] > CMax-1:
        car_y[0] -= CMax
        laptime[laps] = time_str(record - record_temp)
        record_temp = record
        laps += 1
        if laps == GAME_LAPS:
            index = 3
            counter = 0


# 控制電腦賽車
def com_move_car(cs):
    for i in range(cs, CAR):
        if car_spd[i] < 100:
            car_spd[i] += 3
        if i == counter%120:
            car_lr[i] += random.choice([-1, 0, 1])
            if car_lr[i] < -3: car_lr[i] = -3
            if car_lr[i] > 3 : car_lr[i] = 3
        car_x[i] = car_x[i] + car_lr[i]*car_spd[i]/100
        if car_x[i] < 50:
            car_x[i] = 50
            car_lr[i] = int(car_lr[i]*0.9)
        if car_x[i] > 750:
            car_x[i] = 750
            car_lr[i] = int(car_lr[i]*0.9)
        car_y[i] = car_y[i] + car_spd[i]/100
        if car_y[i] > CMax-1:
            car_y[i] -= CMax

        #賽車碰撞
        if index == 2: # 賽車中的碰撞偵測
            cx = car_x[i] - car_x[0]
            cy = car_y[i] - (car_y[0]+PLAYER_CAR_Y)%CMax
            if -100 <= cx and cx <= 100 and -10 <= cy and cy <= 10:
                # 碰撞時的座標變化、交換速度及減速
                car_x[0] -= cx/4
                car_x[i] += cx/4
                car_spd[0], car_spd[i] = car_spd[i]*0.3, car_spd[0]*0.3
                sound_crash.play()


def draw_text(scrn, txt, x, y, col, font):
    sur = font.render(txt, True, BLACK)
    x -= sur.get_width()/2
    y -= sur.get_height()/2
    scrn.blit(sur, [x+2, y+2])
    sur = font.render(txt, True, col)
    scrn.blit(sur, [x, y])


def main():
    global index, counter, sound_crash, laps, record, record_temp, mycar
    pygame.init()
    pygame.display.set_caption('Racer')
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # 字體設定
    font_pixel_s = pygame.font.Font('font/Pixel.ttf', 40)
    font_pixel_m = pygame.font.Font('font/Pixel.ttf', 50)
    font_pixel_l = pygame.font.Font('font/Pixel.ttf', 120)

    img_title = pygame.image.load('image/title.png').convert_alpha()
    img_bg = pygame.image.load('image/bg.png').convert()
    img_sea = pygame.image.load('image/sea.png').convert_alpha()

    img_obj = [
        None,
        pygame.image.load('image/board.png').convert_alpha(),
        pygame.image.load('image/coconut_tree.png').convert_alpha(),
        pygame.image.load('image/yacht.png').convert_alpha()
    ]

    img_car = [
        pygame.image.load("image/car00.png").convert_alpha(),
        pygame.image.load("image/car01.png").convert_alpha(),
        pygame.image.load("image/car02.png").convert_alpha(),
        pygame.image.load("image/car03.png").convert_alpha(),
        pygame.image.load("image/car04.png").convert_alpha(),
        pygame.image.load("image/car05.png").convert_alpha(),
        pygame.image.load("image/car06.png").convert_alpha(),
        pygame.image.load("image/car10.png").convert_alpha(),
        pygame.image.load("image/car11.png").convert_alpha(),
        pygame.image.load("image/car12.png").convert_alpha(),
        pygame.image.load("image/car13.png").convert_alpha(),
        pygame.image.load("image/car14.png").convert_alpha(),
        pygame.image.load("image/car15.png").convert_alpha(),
        pygame.image.load("image/car16.png").convert_alpha(),
        pygame.image.load("image/car20.png").convert_alpha(),
        pygame.image.load("image/car21.png").convert_alpha(),
        pygame.image.load("image/car22.png").convert_alpha(),
        pygame.image.load("image/car23.png").convert_alpha(),
        pygame.image.load("image/car24.png").convert_alpha(),
        pygame.image.load("image/car25.png").convert_alpha(),
        pygame.image.load("image/car26.png").convert_alpha()
    ]

    sound_crash = pygame.mixer.Sound('sound/crash.ogg')  #碰撞音效

    # 計算道路板子的基本形狀
    Board_W = [0]*Board
    Board_H = [0]*Board
    Board_UD = [0]*Board
    for i in range(Board):
        Board_W[i] = 10 + (Board-i)*(Board-i)/12
        Board_H[i] = 3.4*(Board-i)/Board
        Board_UD[i] = 2 * math.sin(math.radians(i * 1.5))

    make_course()
    init_car()

    vertical = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_F1:
                    screen = pygame.display.set_mode((800, 600), FULLSCREEN)
                if event.key == K_F2 or event.key == K_ESCAPE:
                    screen = pygame.display.set_mode((800, 600))

        counter += 1

        # 計算繪製道路用的X座標與路面高低
        di = 0
        ud = 0
        board_x = [0]*Board
        board_ud = [0]*Board
        for i in range(Board):
            di += curve[int(car_y[0]+i)%CMax]
            ud += updown[int(car_y[0]+i)%CMax]
            board_x[i] = 400 - Board_W[i]*car_x[0]/800 + di/2
            board_ud[i] = ud/30

        horizon = 400 + int(ud/3)  # 計算地平線的座標
        sy = horizon  # 開始繪製道路的位置

        vertical = vertical - int(car_spd[0]*di/8000)  # 背景的垂直位置
        if vertical < 0:
            vertical += 800
        if vertical >= 800:
            vertical -= 800

        # 地圖繪製
        screen.fill((0, 56, 255))   # 天空的顏色
        screen.blit(img_bg, [vertical-800, horizon-400])
        screen.blit(img_bg, [vertical, horizon-400])
        screen.blit(img_sea, [board_x[Board-1]-780, sy])   # 最遠的海

        # 根據繪圖資料繪製道路
        for i in range(Board-1, 0, -1):
            ux = board_x[i]
            uy = sy - Board_UD[i]*board_ud[i]
            uw = Board_W[i]
            sy = sy + Board_H[i]*(600-horizon)/200
            bx = board_x[i-1]
            by = sy - Board_UD[i-1]*board_ud[i-1]
            bw = Board_W[i-1]
            col = (160,160,160)
            if int(car_y[0]+i)%CMax == PLAYER_CAR_Y+10:  # 紅線
                col = (192,0,0)
            pygame.draw.polygon(screen, col, [[ux, uy], [ux+uw, uy], [bx+bw, by], [bx, by]])

            # 黃線
            if int(car_y[0]+i)%10 <= 4:
                pygame.draw.polygon(screen, YELLOW, [[ux, uy], [ux+uw*0.02, uy], [bx+bw*0.02, by], [bx, by]])
                pygame.draw.polygon(screen, YELLOW, [[ux + uw * 0.98, uy], [ux + uw, uy], [bx + bw, by], [bx + bw * 0.98, by]])

            # 白線
            if int(car_y[0]+i)%20 <= 10:
                pygame.draw.polygon(screen, WHITE, [[ux + uw * 0.24, uy], [ux + uw * 0.26, uy], [bx + bw * 0.26, by], [bx + bw * 0.24, by]])
                pygame.draw.polygon(screen, WHITE, [[ux + uw * 0.49, uy], [ux + uw * 0.51, uy], [bx + bw * 0.51, by], [bx + bw * 0.49, by]])
                pygame.draw.polygon(screen, WHITE, [[ux + uw * 0.74, uy], [ux + uw * 0.76, uy], [bx + bw * 0.76, by], [bx + bw * 0.74, by]])

            scale = 1.5*Board_W[i]/Board_W[0]

            # 道路左邊的物件
            obj_left = object_left[int(car_y[0]+i) % CMax]
            if obj_left == 2: # 椰子樹
                draw_obj(screen, img_obj[obj_left], ux-uw*0.05, uy, scale)
            if obj_left == 3: # 遊艇
                draw_obj(screen, img_obj[obj_left], ux-uw*0.5, uy, scale)
            if obj_left == 9: # 大海
                screen.blit(img_sea, [ux-uw*0.5-780, uy])

            # 道路右邊的物件
            obj_right = object_right[int(car_y[0]+i) % CMax]
            if obj_right == 1: # 看板
                draw_obj(screen, img_obj[obj_right], ux+uw*1.3, uy, scale)

            # COM賽車
            for c in range(1, CAR):
                if int(car_y[c])%CMax == int(car_y[0]+i)%CMax:
                    lr = int(4*(car_x[0]-car_x[c])/800)  # Player看到COM的方向
                    if lr < -3: lr = -3
                    if lr > 3: lr = 3
                    draw_obj(screen, img_car[(c%3)*7+3+lr], ux+car_x[c]*Board_W[i]/800, uy, 0.05+Board_W[i]/Board_W[0])

            # Player賽車
            if i == PLAYER_CAR_Y:
                draw_shadow(screen, ux + car_x[0] * Board_W[i] / 800, uy, 200 * Board_W[i] / Board_W[0])
                draw_obj(screen, img_car[3 + car_lr[0]+mycar*7], ux + car_x[0] * Board_W[i] / 800, uy, 0.05 + Board_W[i] / Board_W[0])

        draw_text(screen, str(int(car_spd[0])) + 'km/h', 700, 30, RED, font_pixel_m)
        draw_text(screen, "{}/{} 圈".format(laps, GAME_LAPS), 100, 30, WHITE, font_pixel_m)
        draw_text(screen, "時間 "+time_str(record), 130, 80, GREEN, font_pixel_s)
        for i in range(GAME_LAPS):
            draw_text(screen, str(i+1) + '. ' + laptime[i], 110, 130+40*i, YELLOW, font_pixel_s)

        key = pygame.key.get_pressed()

        # 標題畫面、資料初始化
        if index == 0:
            screen.blit(img_title, [250, 120])
            draw_text(screen, "[↑] 開始遊戲", 400, 320, YELLOW, font_pixel_m)
            draw_text(screen, "[S] 挑選車種", 400, 400, YELLOW, font_pixel_m)
            com_move_car(0)
            if key[K_UP] != 0:
                init_car()
                index = 1
                counter = 0
                laps = 0
                record = 0
                record_temp = 0
                for i in range(GAME_LAPS):
                    laptime[i] = "0'00.00"
            if key[K_s] != 0:
                index = 4

        # 遊戲開始倒數
        if index == 1:
            n = 3-int(counter/60)
            draw_text(screen, str(n), 400, 240, YELLOW, font_pixel_l)
            if counter == 179:
                pygame.mixer.music.load('sound/Deja vu.mp3')
                pygame.mixer.music.play(-1)
                index = 2
                counter = 0

        # 遊戲中
        if index == 2:
            if counter < 60:
                draw_text(screen, "Go!", 400, 240, RED, font_pixel_l)
            record = record + 1/60  # 依幀數設定
            drive_car(key)
            com_move_car(1)

        # 抵達終點
        if index == 3:
            if counter == 1:
                pygame.mixer.music.stop()
            if counter == 30:
                pygame.mixer.music.load("sound/goal.ogg")
                pygame.mixer.music.play(0)
            draw_text(screen, "抵達!", 400, 240, GREEN, font_pixel_l)
            car_spd[0] = car_spd[0] * 0.96
            car_y[0] = car_y[0] + car_spd[0]/100
            com_move_car(1)
            if counter > 60*8:
                index = 0

        # 選擇車種
        if index == 4:
            com_move_car(0)
            draw_text(screen, "挑選車種", 400, 160 ,YELLOW, font_pixel_m)
            for i in range(3):
                x = 160+240*i
                y = 300
                col = BLACK
                if i == mycar:
                    col = (0,128,255)
                pygame.draw.rect(screen, col, [x - 100, y - 80, 200, 160])
                draw_text(screen, "[" + str(i + 1) + "]", x, y - 50, YELLOW, font_pixel_m)
                screen.blit(img_car[3+i*7], [x-100, y-20])
            draw_text(screen, "[Enter] OK!", 400, 440, GREEN, font_pixel_m)
            if key[K_1] == 1:
                mycar = 0
            if key[K_2] == 1:
                mycar = 1
            if key[K_3] == 1:
                mycar = 2
            if key[K_RETURN] == 1:
                index = 0

        pygame.display.update()
        clock.tick(60)  # 設定幀數

if __name__ == '__main__':
    main()