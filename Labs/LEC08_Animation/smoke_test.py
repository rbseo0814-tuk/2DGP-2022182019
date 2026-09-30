"""
animation_viewer.py의 Animation 클래스 로직만 따로 검증하는 간단한 테스트.

pico2d 창을 실제로 열지 않고도(=화면 없는 환경에서도) 아래를 확인한다.
- 매니페스트가 정상적으로 로드되는지
- 4개 애니메이션의 프레임 개수가 서로 다른지 (보너스 요건 근거)
- 프레임 크기(w, h)가 애니메이션 내에서 실제로 달라지는지 (보너스 요건 근거)
- Animation이 5회 반복 후 정확히 정지 상태(finished)가 되는지

pico2d 자체는 SDL 렌더러가 있어야 이미지를 불러올 수 있어 완전한 무비디오
테스트는 어렵다. 대신 렌더링과 무관한 "순수 로직" 부분만 pico2d 없이 재현해
검증한다.
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = BASE_DIR / "samurai_manifest.json"


def load_manifest():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


class FakeAnimation:
    """animation_viewer.Animation과 같은 반복/정지 로직만 떼어낸 버전."""

    def __init__(self, frame_count, frame_time=0.05, loop_repeat=5, pause_time=1.0):
        self.frame_count = frame_count
        self.frame_time = frame_time
        self.loop_repeat = loop_repeat
        self.pause_time = pause_time
        self.frame_index = 0
        self.loop_count = 0
        self.timer = 0.0
        self.finished = False

    def update(self, dt):
        if self.finished:
            return
        self.timer += dt
        if self.loop_count < self.loop_repeat:
            if self.timer >= self.frame_time:
                self.timer -= self.frame_time
                self.frame_index += 1
                if self.frame_index >= self.frame_count:
                    self.frame_index = 0
                    self.loop_count += 1
        else:
            if self.timer >= self.pause_time:
                self.finished = True


def check(condition, message):
    status = "OK " if condition else "FAIL"
    print(f"[{status}] {message}")
    return condition


def main():
    manifest = load_manifest()
    animations = manifest["animations"]

    all_ok = True

    all_ok &= check(set(animations.keys()) == {"walk", "run", "jump", "attack"},
                     "walk/run/jump/attack 4종이 모두 있다")

    counts = {name: len(frames) for name, frames in animations.items()}
    all_ok &= check(len(set(counts.values())) > 1,
                     f"애니메이션별 프레임 수가 서로 다르다: {counts}")

    jump_sizes = {(f["w"], f["h"]) for f in animations["jump"]}
    all_ok &= check(len(jump_sizes) > 1,
                     f"jump 애니메이션 안에서 프레임 크기가 달라진다: {len(jump_sizes)}가지")

    # 5회 반복 후 1초 정지가 정확히 일어나는지 시뮬레이션
    anim = FakeAnimation(frame_count=6, frame_time=0.05, loop_repeat=5, pause_time=1.0)
    dt = 0.01
    ticks = 0
    while not anim.finished and ticks < 100000:
        anim.update(dt)
        ticks += 1
    elapsed = ticks * dt
    expected = 6 * 0.05 * 5 + 1.0  # 프레임수 * 프레임시간 * 반복횟수 + 정지시간
    all_ok &= check(anim.finished, "5회 반복 후 정확히 finished 상태가 된다")
    all_ok &= check(abs(elapsed - expected) < 0.05,
                     f"경과 시간이 예상과 비슷하다 (실제 {elapsed:.2f}s / 예상 {expected:.2f}s)")

    print()
    print("전체 통과" if all_ok else "일부 실패")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
