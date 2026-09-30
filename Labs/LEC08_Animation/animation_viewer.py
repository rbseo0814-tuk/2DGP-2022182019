"""
Drill #8. 애니메이션 뷰어

4단계: 캐릭터가 화면 대비 너무 작으므로, 항상 화면 세로의 절반 높이가
       되도록 확대해서 그린다. 프레임마다 원본 크기가 달라도(가변 크기
       스프라이트) 세로 크기를 기준으로 비율을 맞추면 자연스럽게 보인다.
"""
import json
from pathlib import Path

from pico2d import *

BASE_DIR = Path(__file__).resolve().parent
SHEET_PATH = BASE_DIR / "SamuraiSheet.png"
MANIFEST_PATH = BASE_DIR / "samurai_manifest.json"

CANVAS_W, CANVAS_H = 960, 640
TARGET_HEIGHT_RATIO = 0.5  # 캐릭터 표시 높이 = 화면 세로 * 이 값


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


def main():
    open_canvas(CANVAS_W, CANVAS_H)

    sheet = load_image(str(SHEET_PATH))
    manifest = load_manifest()
    sheet_h = manifest["sheet_size"][1]

    walk_frames = manifest["animations"]["walk"]
    rects = [to_pico_rect(f, sheet_h) for f in walk_frames]

    target_height = CANVAS_H * TARGET_HEIGHT_RATIO
    # 프레임마다 원본 (w, h)가 다르므로, 화면에 그릴 크기도 프레임마다 따로 계산한다.
    draw_sizes = []
    for (_, _, w, h) in rects:
        scale = target_height / h
        draw_sizes.append((round(w * scale), round(h * scale)))

    frame_index = 0
    for _ in range(200):  # 임시로 200틱만 재생하고 종료 (무한 재생은 다음 단계에서)
        left, bottom, w, h = rects[frame_index]
        draw_w, draw_h = draw_sizes[frame_index]

        clear_canvas()
        sheet.clip_draw(left, bottom, w, h, CANVAS_W // 2, CANVAS_H // 2, draw_w, draw_h)
        update_canvas()
        delay(0.1)

        frame_index = (frame_index + 1) % len(rects)

    close_canvas()


if __name__ == "__main__":
    main()
