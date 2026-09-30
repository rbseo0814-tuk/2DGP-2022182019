"""
Drill #8. 애니메이션 뷰어 (AI 이용한 개발)

[에셋]
- 수업 자료 폴더에 제공된 SamuraiSheet.png를 그대로 사용한다.
- build_manifest.py가 알파 채널을 분석해 각 동작(행)에서 실제 그림이 있는
  영역만 타이트하게 잘라내 samurai_manifest.json을 만든다 (자세한 과정은
  build_manifest.py와 README.md 참고).

[요구사항 대응]
- 최소 4종 애니메이션: walk / run / jump(구르기) / attack (ANIM_ORDER)
- 화면 절반 이상으로 확대: TARGET_HEIGHT_RATIO(=0.5)만큼 항상 확대해서 그림
- 화면 중앙 재생: 가로는 CANVAS_W//2, 세로는 baseline_y로 고정
- 5회 반복 후 1초 정지, 이후 다음 애니메이션으로 무한 순환
  (Animation 클래스의 loop_repeat / pause_time / finished 참고)

[보너스 - 명시 사항]
1) "프레임마다 크기가 달라지는 복잡한 Sprite Sheet"
   -> samurai_manifest.json의 각 프레임은 균일한 그리드가 아니라, 알파 채널
      기준으로 실제 그림 크기(w, h)를 각각 계산해 저장한 값이다. 특히 jump
      애니메이션은 프레임마다 세로 크기가 80~63px까지 실제로 달라진다.
      Animation.__init__()은 이 서로 다른 (w, h)를 그대로 받아 프레임별로
      확대 비율을 따로 계산하며, draw()는 baseline_y 기준으로 높이가 달라도
      발 위치가 흔들리지 않게 그린다.
2) "애니메이션별 프레임 수가 서로 다른 경우 지원"
   -> walk=8, run=8, jump=12, attack=6 으로 프레임 개수가 서로 다르다.
      Animation은 frames 리스트의 길이를 그대로 쓰므로 개수가 몇 개든 동작한다.
"""
import json
import os
from itertools import cycle
from pathlib import Path

import pico2d
from pico2d import *

BASE_DIR = Path(__file__).resolve().parent
SHEET_PATH = BASE_DIR / "SamuraiSheet.png"
MANIFEST_PATH = BASE_DIR / "samurai_manifest.json"

CANVAS_W, CANVAS_H = 960, 640
TARGET_HEIGHT_RATIO = 0.5  # 캐릭터 표시 높이 = 화면 세로 * 이 값
FRAME_TIME = 0.09          # 기본 프레임 재생 시간(초) - 아래 표에 없는 동작에 쓰는 기본값
LOOP_REPEAT = 5            # 한 애니메이션을 몇 번 반복한 뒤 쉴지
PAUSE_TIME = 1.0           # 반복 후 정지 시간(초)

# 최소 4종 요구사항: 걷기/뛰기/구르기(점프)/공격 순서로 무한 반복한다.
ANIM_ORDER = ["walk", "run", "jump", "attack"]

# 동작마다 자연스러운 체감 속도가 다르다(조교 공지: "너무 빠르거나 느리지
# 않도록 자연스러운 속도로 설정"). 프레임 개수가 다르므로 FRAME_TIME도
# 동작별로 따로 맞춘다 - 걷기/달리기는 발걸음이 보일 정도로 느긋하게,
# 구르기·공격은 순간 동작이라 더 빠르게 넘긴다.
FRAME_TIME_BY_ANIM = {
    "walk": 0.10,
    "run": 0.07,
    "jump": 0.06,
    "attack": 0.08,  # 원래 0.045였는데 너무 빨라 보여서 늦췄다
}

# 라벨이 영문뿐이라 굳이 한글 폰트가 필요하진 않지만, 특정 OS/설치 환경에만
# 있는 "C:/Windows/Fonts/..." 같은 절대경로 대신 pico2d 패키지에 이미 들어있는
# 폰트를 써서 pico2d만 설치돼 있으면 어떤 컴퓨터에서도 그대로 동작하게 한다.
FONT_PATH = os.path.join(os.path.dirname(pico2d.__file__), "data", "ConsolaMalgun.ttf")


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
        frame_time = FRAME_TIME_BY_ANIM.get(name, FRAME_TIME)
        return Animation(manifest["animations"][name], sheet_h, target_height,
                          frame_time=frame_time)

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
        font.draw(20, CANVAS_H - 36, current_name, (20, 20, 20))
        update_canvas()
        delay(0.01)

    close_canvas()


if __name__ == "__main__":
    main()
