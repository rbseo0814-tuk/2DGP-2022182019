import os
import sys

from pico2d import *


# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
CANVAS_W, CANVAS_H = 800, 600
FRAME_DELAY = 0.01           # 메인 루프 한 바퀴마다 쉬는 시간(초)
FRAME_TIME = 0.12            # 애니메이션 프레임 하나를 보여주는 시간(초)

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

frames = ACTIONS[0][1]
frame = 0
frame_timer = 0.0
prev_time = get_time()

running = True
while running:
    running = handle_events()

    # 경과 시간만큼 타이머를 채우고, FRAME_TIME이 찰 때마다 다음 프레임으로 넘긴다.
    now = get_time()
    frame_timer += now - prev_time
    prev_time = now
    while frame_timer >= FRAME_TIME:
        frame_timer -= FRAME_TIME
        frame = (frame + 1) % len(frames)

    clear_canvas()
    left, bottom, w, h = frames[frame]
    sheet.clip_draw(left, bottom, w, h, CANVAS_W // 2, CANVAS_H // 2)
    update_canvas()
    delay(FRAME_DELAY)

close_canvas()
