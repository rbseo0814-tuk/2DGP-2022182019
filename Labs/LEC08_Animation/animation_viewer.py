"""
Drill #8. 애니메이션 뷰어

10단계: clip_draw(..., x, y)는 프레임의 '중심'을 (x, y)에 맞춘다.
        그런데 jump 애니메이션처럼 프레임마다 높이가 크게 다르면, 중심을
        맞출 때 발 위치가 위아래로 흔들려 보인다(웅크릴수록 발이 뜸).
        대신 '바닥선(baseline)'을 고정하고 그 위에 발이 닿도록 그리면
        캐릭터가 제자리에 서 있는 것처럼 자연스럽다.
"""
import json
from itertools import cycle
from pathlib import Path

from pico2d import *

BASE_DIR = Path(__file__).resolve().parent
SHEET_PATH = BASE_DIR / "SamuraiSheet.png"
MANIFEST_PATH = BASE_DIR / "samurai_manifest.json"

CANVAS_W, CANVAS_H = 960, 640
TARGET_HEIGHT_RATIO = 0.5  # 캐릭터 표시 높이 = 화면 세로 * 이 값
FRAME_TIME = 0.09          # 한 프레임을 보여주는 시간(초)
LOOP_REPEAT = 5            # 한 애니메이션을 몇 번 반복한 뒤 쉴지
PAUSE_TIME = 1.0           # 반복 후 정지 시간(초)

# 최소 4종 요구사항: 걷기/뛰기/구르기(점프)/공격 순서로 무한 반복한다.
ANIM_ORDER = ["walk", "run", "jump", "attack"]

FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
LABEL_TEXT = {
    "walk": "걷기 (walk)",
    "run": "달리기 (run)",
    "jump": "구르기 (jump)",
    "attack": "공격 (attack)",
}


def load_manifest():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def to_pico_rect(frame, sheet_h):
    """
    매니페스트의 (x, y, w, h)는 Pillow 기준 '왼쪽-위'가 원점이다.
    pico2d의 clip_draw는 '왼쪽-아래'가 원점이므로 y를 뒤집어 변환한다.
    """
    left = frame["x"]
    width = frame["w"]
    height = frame["h"]
    bottom = sheet_h - (frame["y"] + height)
    return left, bottom, width, height


class Animation:
    """
    하나의 동작(walk 등)을 재생하는 상태를 관리한다.
    - 프레임마다 원본 크기가 달라도 항상 같은 표시 높이로 그린다.
    - update(dt)를 호출해서 시간이 흐른 만큼 다음 프레임으로 넘어가게 한다.
    """

    def __init__(self, frames, sheet_h, target_height,
                 frame_time=FRAME_TIME, loop_repeat=LOOP_REPEAT, pause_time=PAUSE_TIME):
        self.rects = [to_pico_rect(f, sheet_h) for f in frames]
        self.draw_sizes = []
        for (_, _, w, h) in self.rects:
            scale = target_height / h
            self.draw_sizes.append((round(w * scale), round(h * scale)))

        self.frame_time = frame_time
        self.loop_repeat = loop_repeat
        self.pause_time = pause_time

        self.frame_index = 0
        self.loop_count = 0
        self.timer = 0.0
        self.finished = False  # loop_repeat번 반복 + 정지까지 모두 끝났는지

    def update(self, dt):
        if self.finished:
            return
        self.timer += dt
        if self.loop_count < self.loop_repeat:
            # 아직 반복 중: 프레임을 계속 넘긴다.
            if self.timer >= self.frame_time:
                self.timer -= self.frame_time
                self.frame_index += 1
                if self.frame_index >= len(self.rects):
                    self.frame_index = 0
                    self.loop_count += 1
        else:
            # 반복을 다 채웠으니 마지막 프레임을 보여준 채로 잠깐 정지한다.
            if self.timer >= self.pause_time:
                self.finished = True

    def draw(self, image, cx, baseline_y):
        """
        cx: 가로 중심. baseline_y: 발이 닿는 바닥선(세로 기준점).
        clip_draw는 (x, y)를 사각형의 '중심'으로 쓰므로, 발이 baseline_y에
        오도록 하려면 그 프레임의 표시 높이 절반만큼 위로 올려서 중심을 잡는다.
        """
        left, bottom, w, h = self.rects[self.frame_index]
        draw_w, draw_h = self.draw_sizes[self.frame_index]
        cy = baseline_y + draw_h / 2
        image.clip_draw(left, bottom, w, h, cx, cy, draw_w, draw_h)


def handle_events():
    """창 닫기 버튼 또는 ESC 키가 눌리면 False를 반환해 메인 루프를 끝낸다."""
    for event in get_events():
        if event.type == SDL_QUIT:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
    return True


def main():
    open_canvas(CANVAS_W, CANVAS_H)

    sheet = load_image(str(SHEET_PATH))
    manifest = load_manifest()
    sheet_h = manifest["sheet_size"][1]
    target_height = CANVAS_H * TARGET_HEIGHT_RATIO
    font = load_font(FONT_PATH, 24)

    order = [name for name in ANIM_ORDER if name in manifest["animations"]]
    anim_cycle = cycle(order)

    def make_animation(name):
        return Animation(manifest["animations"][name], sheet_h, target_height)

    current_name = next(anim_cycle)
    current = make_animation(current_name)

    # 가장 큰 프레임(target_height)이 화면 세로 중앙에 오도록 바닥선을 고정한다.
    baseline_y = CANVAS_H // 2 - target_height / 2

    running = True
    while running:
        running = handle_events()

        current.update(0.01)
        if current.finished:
            current_name = next(anim_cycle)
            current = make_animation(current_name)

        clear_canvas()
        current.draw(sheet, CANVAS_W // 2, baseline_y)
        font.draw(20, CANVAS_H - 36, f"현재 동작: {LABEL_TEXT[current_name]}", (20, 20, 20))
        update_canvas()
        delay(0.01)

    close_canvas()


if __name__ == "__main__":
    main()
