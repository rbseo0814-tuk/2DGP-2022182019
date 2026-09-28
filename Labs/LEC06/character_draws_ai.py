# 실습 과제 진행 (AI 버전)
from pico2d import *
import math

open_canvas(800, 600)
character = load_image('character.png')

DELAY_TIME = 0.01
CENTER_X, CENTER_Y = 400, 300
RADIUS = 200

# 캔버스를 지우고 (x, y)에 캐릭터를 그림
def draw_character(x, y):
    clear_canvas()
    character.draw(x, y)
    update_canvas()
    delay(DELAY_TIME)

# 중심을 기준으로 원을 그리며 이동
def move_circle():
    for degree in range(360):
        theta = math.radians(degree)
        x = CENTER_X + RADIUS * math.cos(theta)
        y = CENTER_Y + RADIUS * math.sin(theta)
        draw_character(x, y)

def move_top():
    for x in range(50, 751, 5):
        draw_character(x, 550)

def move_right():
    for y in range(550, 49, -5):
        draw_character(750, y)

def move_bottom():
    for x in range(750, 49, -5):
        draw_character(x, 50)

def move_left():
    for y in range(50, 551, 5):
        draw_character(50, y)

# 상 -> 우 -> 하 -> 좌 순서로 사각형 이동
def move_rectangle():
    move_top()
    move_right()
    move_bottom()
    move_left()

# 대각선 두 변을 따라 삼각형 이동
def move_triangle():
    for x in range(50, 751, 5):
        y = 50 + (x - 50) * (500 / 700)
        draw_character(x, y)

    for x in range(750, 49, -5):
        y = 550 - (x - 50) * (500 / 700)
        draw_character(x, y)

while True:
    move_circle()
    move_rectangle()
    move_triangle()
