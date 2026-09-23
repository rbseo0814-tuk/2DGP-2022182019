from pico2d import *
import math

open_canvas(800, 600)
character = load_image('character.png')

clear_canvas()
character.draw(400, 300)
update_canvas()
delay(1)
close_canvas()

def move_circle():
    for degree in range(360):
        

def move_rectangle():
    print('rectangle')

def move_triangle():
    print('triangle')

while True:
    move_circle()
    move_rectangle()
    move_triangle()
    pass