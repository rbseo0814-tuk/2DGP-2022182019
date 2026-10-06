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


# ---------------------------------------------------------------------------
# 프레임 데이터
#   각 프레임은 (left, bottom, width, height) — pico2d 좌표계(좌하단 원점).
#   시트의 알파 채널에서 실제 그림이 있는 영역을 측정한 값이다.
# ---------------------------------------------------------------------------
ACTIONS = [
    ("Idle", [
        (1, 447, 29, 39), (31, 447, 26, 38), (58, 447, 29, 39),
        (87, 447, 29, 39), (118, 447, 30, 38), (150, 447, 30, 38),
        (182, 447, 30, 39),
    ]),
]


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
    left, bottom, w, h = ACTIONS[0][1][0]
    sheet.clip_draw(left, bottom, w, h, CANVAS_W // 2, CANVAS_H // 2)
    update_canvas()
    delay(FRAME_DELAY)

close_canvas()
