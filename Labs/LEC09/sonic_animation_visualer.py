from pico2d import *


# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
CANVAS_W, CANVAS_H = 800, 600
FRAME_DELAY = 0.01           # 메인 루프 한 바퀴마다 쉬는 시간(초)


def handle_events():
    """창 닫기 버튼이나 ESC 키가 눌리면 False를 돌려준다."""
    for event in get_events():
        if event.type == SDL_QUIT:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
    return True


open_canvas(CANVAS_W, CANVAS_H)

running = True
while running:
    running = handle_events()

    clear_canvas()
    update_canvas()
    delay(FRAME_DELAY)

close_canvas()
