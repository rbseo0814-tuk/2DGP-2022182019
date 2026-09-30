"""
Drill #8. 애니메이션 뷰어

6단계: 요구사항인 "5회 반복 후 1초 정지"를 Animation 클래스에 추가한다.
       지정한 횟수만큼 다 돌면 스스로 '정지 상태'가 되고, finished 플래그로
       바깥(main)에 알려준다.
"""
import json
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

    def draw(self, image, cx, cy):
        left, bottom, w, h = self.rects[self.frame_index]
        draw_w, draw_h = self.draw_sizes[self.frame_index]
        image.clip_draw(left, bottom, w, h, cx, cy, draw_w, draw_h)


def main():
    open_canvas(CANVAS_W, CANVAS_H)

    sheet = load_image(str(SHEET_PATH))
    manifest = load_manifest()
    sheet_h = manifest["sheet_size"][1]
    target_height = CANVAS_H * TARGET_HEIGHT_RATIO

    walk = Animation(manifest["animations"]["walk"], sheet_h, target_height)

    # walk가 5회 반복 + 1초 정지까지 끝낼 때까지만 재생 (다음 단계에서 무한 순환으로 확장)
    while not walk.finished:
        walk.update(0.01)

        clear_canvas()
        walk.draw(sheet, CANVAS_W // 2, CANVAS_H // 2)
        update_canvas()
        delay(0.01)

    close_canvas()


if __name__ == "__main__":
    main()
