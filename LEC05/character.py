from pico2d import*
import math

open_canvas(900, 600)
character = load_image('character.png')

cx = 450
cy = 300
r = 200
theta = 0

while (1):
    clear_canvas()
    x = cx + r * math.cos(theta)
    y = cy + r * math.sin(theta)

    character.draw(x, y)
    update_canvas()

    theta += 0.05
    delay(0.01)
    

close_canvas()