# 실습 과제 진행
import os
from pico2d import *

script_dir = os.path.dirname(os.path.abspath(__file__))

open_canvas(800, 600)
character = load_image(os.path.join(script_dir, 'character.png'))


def move_circle():
    print("circle")
    pass

def move_rectangle():
    print("rectangle")
    pass

def move_triangle():
    print("triangle")
    pass

while True:
    move_circle()
    move_rectangle()
    move_triangle()
    pass