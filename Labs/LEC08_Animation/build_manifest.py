"""
SamuraiSheet.png 분석 1단계: 알파 채널을 기준으로 "행(row)" 단위 애니메이션 묶음을 찾는다.

스프라이트 시트는 투명 배경 위에 동작별로 한 줄씩 캐릭터가 나열되어 있다.
행과 행 사이에는 완전히 투명한 빈 줄이 있으므로, 세로 방향으로 스캔하면서
"내용이 있는 구간"만 모으면 자동으로 몇 개의 애니메이션이 들어있는지 알 수 있다.
"""
from pathlib import Path

import numpy as np
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
SHEET_PATH = BASE_DIR / "SamuraiSheet.png"
ALPHA_THRESHOLD = 10  # 이 값보다 큰 알파만 "그림이 있다"고 본다


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


def main():
    image = Image.open(SHEET_PATH).convert("RGBA")
    alpha = np.array(image)[:, :, 3]
    content = alpha > ALPHA_THRESHOLD

    row_has_content = content.any(axis=1)
    row_bands = find_bands(row_has_content)

    print(f"시트 크기: {image.size}")
    print(f"감지된 행(애니메이션) 개수: {len(row_bands)}")
    for i, (y0, y1) in enumerate(row_bands):
        print(f"  row {i}: y=({y0},{y1})  height={y1 - y0}")


if __name__ == "__main__":
    main()
