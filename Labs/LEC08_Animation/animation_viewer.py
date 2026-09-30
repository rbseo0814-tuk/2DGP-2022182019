"""
Drill #8. 애니메이션 뷰어

이 파일은 앞으로 여러 커밋에 걸쳐 조금씩 완성해 나간다.
1단계: pico2d 캔버스를 열고 닫기만 한다.
"""
from pico2d import *

CANVAS_W, CANVAS_H = 960, 640


def main():
    open_canvas(CANVAS_W, CANVAS_H)
    close_canvas()


if __name__ == "__main__":
    main()
