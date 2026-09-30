"""
Drill #8. 애니메이션 뷰어

2단계: 스프라이트 시트와 매니페스트(JSON)를 불러와서,
       그 중 한 프레임만 화면에 정적으로 그려서 좌표 변환이 맞는지 확인한다.
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

    # 확인용: walk 애니메이션의 첫 번째 프레임 하나만 그려본다.
    first_frame = manifest["animations"]["walk"][0]
    left, bottom, w, h = to_pico_rect(first_frame, sheet_h)

    clear_canvas()
    sheet.clip_draw(left, bottom, w, h, CANVAS_W // 2, CANVAS_H // 2)
    update_canvas()
    delay(3)

    close_canvas()


if __name__ == "__main__":
    main()
