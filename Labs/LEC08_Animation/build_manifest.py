"""
SamuraiSheet.png 분석 1단계: 알파 채널을 기준으로 "행(row)" 단위 애니메이션 묶음을 찾는다.

스프라이트 시트는 투명 배경 위에 동작별로 한 줄씩 캐릭터가 나열되어 있다.
행과 행 사이에는 완전히 투명한 빈 줄이 있으므로, 세로 방향으로 스캔하면서
"내용이 있는 구간"만 모으면 자동으로 몇 개의 애니메이션이 들어있는지 알 수 있다.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
SHEET_PATH = BASE_DIR / "SamuraiSheet.png"
MANIFEST_PATH = BASE_DIR / "samurai_manifest.json"
ALPHA_THRESHOLD = 10  # 이 값보다 큰 알파만 "그림이 있다"고 본다

# 시트에 있는 10개 행(대기/걷기/달리기/구르기/공격x3/피격/대기2/사망) 중
# 과제에서 요구하는 "최소 4종"에 맞춰 이름을 붙여 사용할 4개만 고른다.
# row 인덱스는 build_manifest.py를 실행해 나온 순서 그대로.
ROW_NAMES = {
    1: "walk",
    2: "run",
    3: "jump",    # 구르기 동작 - 프레임마다 크기가 눈에 띄게 다름
    4: "attack",
}

# 일부 동작(칼을 휘두르는 공격)에는 캐릭터 그림 옆에 작은 '궤적(잔상)' 표시가
# 별도의 투명 조각으로 떨어져 있다. 알파 채널만 보면 이것도 하나의 "프레임"으로
# 잘못 검출되므로, 실제로 크롭 이미지를 눈으로 확인한 뒤 제외 목록에 적어둔다.
# (row 인덱스, 그 행에서 몇 번째로 검출된 조각인지) -> 캐릭터가 아니라 이펙트임
EXCLUDE_FRAGMENTS = {
    4: [5],  # attack 동작 5번째칸과 6번째칸 사이의 얇은 곡선 이펙트
    5: [3],  # attack 동작 3번째칸과 4번째칸 사이의 작은 이펙트
}


def find_bands(has_content):
    """1차원 불리언 배열에서 True가 연속되는 구간(시작,끝)의 목록을 반환."""
    bands = []
    in_band = False
    start = 0
    for i, v in enumerate(has_content):
        if v and not in_band:
            start = i
            in_band = True
        if not v and in_band:
            bands.append((start, i))
            in_band = False
    if in_band:
        bands.append((start, len(has_content)))
    return bands


def find_frames_in_row(content, y0, y1):
    """한 행(row) 안에서 가로 방향으로 내용이 있는 구간 = 개별 프레임들을 찾는다."""
    row_slice = content[y0:y1, :]
    col_has_content = row_slice.any(axis=0)
    return find_bands(col_has_content)


def tight_bbox(content, x0, x1, y0, y1):
    """
    (x0,x1) x (y0,y1) 영역 안에서 실제로 그림이 있는 부분만 딱 맞게 잘라낸
    사각형(x, y, w, h)을 구한다. row 전체 높이를 그대로 쓰지 않고 프레임마다
    다시 계산하므로, 크기가 작은 포즈(예: 웅크리기)는 실제로 더 작은 사각형이 된다.
    """
    region = content[y0:y1, x0:x1]
    ys, xs = np.nonzero(region)
    left = x0 + int(xs.min())
    right = x0 + int(xs.max()) + 1
    top = y0 + int(ys.min())
    bottom = y0 + int(ys.max()) + 1
    return {"x": left, "y": top, "w": right - left, "h": bottom - top}


def build_animation(content, row_index, y0, y1):
    """한 행에서 이름 붙일 애니메이션의 프레임 목록(타이트 바운딩 박스)을 만든다."""
    frames = find_frames_in_row(content, y0, y1)
    excluded = set(EXCLUDE_FRAGMENTS.get(row_index, []))
    result = []
    for j, (x0, x1) in enumerate(frames):
        if j in excluded:
            continue
        result.append(tight_bbox(content, x0, x1, y0, y1))
    return result


def main():
    image = Image.open(SHEET_PATH).convert("RGBA")
    alpha = np.array(image)[:, :, 3]
    content = alpha > ALPHA_THRESHOLD

    row_has_content = content.any(axis=1)
    row_bands = find_bands(row_has_content)

    print(f"시트 크기: {image.size}")
    print(f"감지된 행(애니메이션) 개수: {len(row_bands)}")

    animations = {}
    for row_index, name in ROW_NAMES.items():
        y0, y1 = row_bands[row_index]
        frames = build_animation(content, row_index, y0, y1)
        animations[name] = frames
        sizes = [(f["w"], f["h"]) for f in frames]
        print(f"  [{name}] row {row_index}: 프레임 {len(frames)}개  크기(w,h)들={sizes}")

    manifest = {
        "sheet": SHEET_PATH.name,
        "sheet_size": list(image.size),
        "animations": animations,
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n매니페스트 저장 완료: {MANIFEST_PATH.name}")


if __name__ == "__main__":
    main()
