import os
import sys

from pico2d import *


# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
CANVAS_W, CANVAS_H = 800, 600
FRAME_DELAY = 0.01           # 메인 루프 한 바퀴마다 쉬는 시간(초)
FRAME_TIME = 0.12            # 애니메이션 프레임 하나를 보여주는 시간(초)
TARGET_HEIGHT_RATIO = 0.5    # 동작의 가장 큰 프레임이 화면 높이에서 차지할 비율
BASELINE_Y = 150             # 캐릭터 발(바닥선)이 놓일 화면 y 좌표
REPEAT_COUNT = 5             # 동작 하나를 반복 재생하는 횟수
REST_TIME = 1.0              # 반복을 마친 뒤 다음 동작까지 쉬는 시간(초)

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
    ("Look Up", [(212, 447, 28, 39), (240, 447, 29, 39)]),
    ("Duck", [(270, 448, 24, 32), (302, 448, 29, 26)]),
    ("Walk", [
        (8, 408, 26, 37), (37, 408, 27, 37), (65, 407, 31, 38),
        (97, 408, 37, 37), (135, 410, 32, 35), (170, 408, 32, 38),
        (206, 408, 26, 38), (238, 408, 24, 37),
    ]),
    ("Jog", [
        (263, 408, 30, 37), (295, 408, 36, 37), (334, 409, 32, 36),
        (370, 408, 29, 38),
    ]),
    ("Run", [
        (1, 361, 33, 40), (39, 362, 35, 39), (89, 362, 35, 38),
        (130, 362, 34, 42),
    ]),
    ("Kick", [(181, 362, 34, 41), (228, 363, 33, 40)]),
]


def load_sprite_sheet():
    if not os.path.isfile(SPRITE_PATH):
        sys.exit(f"스프라이트 이미지를 찾을 수 없습니다: {SPRITE_PATH}")
    return load_image(SPRITE_PATH)


def compute_scale(frames):
    """동작 하나에 쓸 정수 확대 배율.

    프레임마다 배율이 바뀌면 캐릭터 크기가 출렁이므로 동작 단위로 한 번만 정한다.
    정수 배율이라 픽셀 아트가 흐려지지 않는다.
    """
    max_h = max(h for _, _, _, h in frames)
    return max(1, int(CANVAS_H * TARGET_HEIGHT_RATIO) // max_h)


def draw_frame(image, rect, scale, base_bottom):
    """프레임을 가로 중앙, 바닥선 기준으로 확대해서 그린다.

    시트에서 같은 동작의 프레임들은 같은 지면 위에 놓여 있으므로,
    가장 낮은 프레임(base_bottom)과의 높이 차이를 그대로 유지해 그리면
    프레임 높이가 달라도 발 위치가 흔들리지 않는다.
    """
    left, bottom, w, h = rect
    draw_w, draw_h = w * scale, h * scale
    y = BASELINE_Y + (bottom - base_bottom) * scale + draw_h / 2
    image.clip_draw(left, bottom, w, h, CANVAS_W / 2, y, draw_w, draw_h)


def handle_events():
    """창 닫기 버튼이나 ESC 키가 눌리면 False를 돌려준다."""
    for event in get_events():
        if event.type == SDL_QUIT:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
    return True


class AnimationPlayer:
    """재생 상태(현재 동작, 프레임, 반복 횟수, 타이머)를 관리한다."""

    def __init__(self, actions):
        self.actions = actions
        self.action_index = 0
        self.frame = 0
        self.frame_timer = 0.0
        self.play_count = 0          # 현재 동작을 끝까지 재생한 횟수
        self.resting = False         # REPEAT_COUNT회 재생을 마치고 쉬는 중인지
        self.rest_timer = 0.0
        self._prepare_action()

    def _prepare_action(self):
        _, frames = self.actions[self.action_index]
        self.frames = frames
        self.scale = compute_scale(frames)
        self.base_bottom = min(b for _, b, _, _ in frames)

    def update(self, dt):
        if self.resting:
            self.rest_timer += dt
            if self.rest_timer >= REST_TIME:
                self._next_action()
            return

        # 경과 시간만큼 타이머를 채우고, FRAME_TIME이 찰 때마다 다음 프레임으로 넘긴다.
        self.frame_timer += dt
        while self.frame_timer >= FRAME_TIME and not self.resting:
            self.frame_timer -= FRAME_TIME
            self._advance_frame()

    def _advance_frame(self):
        if self.frame < len(self.frames) - 1:
            self.frame += 1
            return

        # 마지막 프레임까지 보여줬으면 1회 재생 완료.
        self.play_count += 1
        if self.play_count >= REPEAT_COUNT:
            self.resting = True      # 쉬는 동안 마지막 프레임을 그대로 보여준다.
        else:
            self.frame = 0

    def _next_action(self):
        # 마지막 동작 다음에는 첫 동작으로 돌아가 무한 반복한다.
        self.action_index = (self.action_index + 1) % len(self.actions)
        self.frame = 0
        self.frame_timer = 0.0
        self.play_count = 0
        self.resting = False
        self.rest_timer = 0.0
        self._prepare_action()

    def draw(self, image):
        draw_frame(image, self.frames[self.frame], self.scale, self.base_bottom)


def main():
    open_canvas(CANVAS_W, CANVAS_H)
    sheet = load_sprite_sheet()
    player = AnimationPlayer(ACTIONS)

    prev_time = get_time()
    running = True
    while running:
        running = handle_events()

        now = get_time()
        player.update(now - prev_time)
        prev_time = now

        clear_canvas()
        player.draw(sheet)
        update_canvas()
        delay(FRAME_DELAY)

    close_canvas()


if __name__ == "__main__":
    main()
