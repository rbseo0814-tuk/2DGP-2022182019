from pico2d import *


# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
CANVAS_W, CANVAS_H = 800, 600
FRAME_DELAY = 0.01           # 메인 루프 한 바퀴마다 쉬는 시간(초)


open_canvas(CANVAS_W, CANVAS_H)

running = True
while running:
    for event in get_events():
        if event.type == SDL_QUIT:
            running = False

    clear_canvas()
    update_canvas()
    delay(FRAME_DELAY)

close_canvas()
