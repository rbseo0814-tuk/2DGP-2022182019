import os
import sys

from pico2d import *


# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
CANVAS_W, CANVAS_H = 800, 600
FRAME_DELAY = 0.01           # 메인 루프 한 바퀴마다 쉬는 시간(초)

# 어느 디렉터리에서 실행하든 스크립트 옆의 이미지를 찾도록 절대 경로로 만든다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITE_PATH = os.path.join(BASE_DIR, "sonic-sprite.png")


def load_sprite_sheet():
    if not os.path.isfile(SPRITE_PATH):
        sys.exit(f"스프라이트 이미지를 찾을 수 없습니다: {SPRITE_PATH}")
    return load_image(SPRITE_PATH)


def handle_events():
    """창 닫기 버튼이나 ESC 키가 눌리면 False를 돌려준다."""
    for event in get_events():
        if event.type == SDL_QUIT:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
    return True


open_canvas(CANVAS_W, CANVAS_H)
sheet = load_sprite_sheet()

running = True
while running:
    running = handle_events()

    clear_canvas()
    # 좌표 확인용: 시트 전체를 원본 크기로 화면 중앙에 그린다.
    sheet.draw(CANVAS_W // 2, CANVAS_H // 2)
    update_canvas()
    delay(FRAME_DELAY)

close_canvas()
