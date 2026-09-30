"""
Drill #8. 애니메이션 뷰어

3단계: walk 애니메이션의 프레임을 순서대로 계속 바꿔가며 재생해본다.
       (아직 확대·중앙정렬·반복횟수 제한은 없음 - 뼈대만 확인)
"""
import json
from pathlib import Path

from pico2d import *

BASE_DIR = Path(__file__).resolve().parent
SHEET_PATH = BASE_DIR / "SamuraiSheet.png"
MANIFEST_PATH = BASE_DIR / "samurai_manifest.json"

CANVAS_W, CANVAS_H = 960, 640


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

    frame_index = 0
    for _ in range(200):  # 임시로 200틱만 재생하고 종료 (무한 재생은 다음 단계에서)
        left, bottom, w, h = rects[frame_index]

        clear_canvas()
        sheet.clip_draw(left, bottom, w, h, CANVAS_W // 2, CANVAS_H // 2)
        update_canvas()
        delay(0.1)

        frame_index = (frame_index + 1) % len(rects)

    close_canvas()


if __name__ == "__main__":
    main()
