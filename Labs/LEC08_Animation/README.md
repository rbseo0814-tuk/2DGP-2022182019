# Drill #8. 애니메이션 뷰어

## 실행 방법
```
cd Labs/LEC08_Animation
python animation_viewer.py
```
`pico2d`, `Pillow` 가 필요합니다 (`pip install pico2d pillow`).
ESC 키 또는 창 닫기 버튼으로 종료합니다.

## 파일 구성
| 파일 | 역할 |
|---|---|
| `animation_viewer.py` | 제출 대상. 애니메이션 뷰어 본체 |
| `SamuraiSheet.png` | 수업 자료 폴더에 제공된 스프라이트 시트 (원본 그대로 사용) |
| `build_manifest.py` | `SamuraiSheet.png`을 분석해 `samurai_manifest.json`을 생성하는 스크립트 |
| `samurai_manifest.json` | `build_manifest.py`의 결과물. 애니메이션별 프레임 좌표/크기 |
| `smoke_test.py` | pico2d 창 없이 로직(반복·정지, 매니페스트 속성)을 확인하는 테스트 |
| `PLAN.md` | 작업 계획 메모 |

## 에셋 준비 방법 (AI 이용한 개발)
`SamuraiSheet.png`는 수업 자료로 이미 제공되어 있던 파일을 그대로 사용했습니다.
다만 이 시트는 프레임 크기가 균일하지 않고(자유 배치), 동작마다 프레임 개수도
달라서 "그리드를 일정 칸으로 나눠 자르기" 방식으로는 쓸 수 없었습니다.

그래서 `build_manifest.py`를 작성해 AI(알파 채널 분석)로 시트 구조를 스스로
찾아내도록 했습니다.
1. 이미지를 세로로 스캔해서 완전히 투명한 빈 줄로 구분되는 "행(하나의 동작)"을 찾는다.
2. 각 행 안에서 다시 가로로 스캔해 "프레임(칸)"을 찾는다.
3. 칼을 휘두를 때 생기는 궤적 이펙트가 별도 조각으로 검출되는 경우가 있어,
   크롭 이미지를 직접 눈으로 확인하고 이런 조각만 제외했다 (`EXCLUDE_FRAGMENTS`).
4. 프레임마다 "실제로 그림이 있는 영역"만 딱 맞게 잘라(`tight_bbox`) 좌표를
   `samurai_manifest.json`에 저장한다.

결과를 재현하려면:
```
python build_manifest.py
```

## 요구사항 대응
- **애니메이션 4종 이상**: walk(걷기) / run(달리기) / jump(구르기) / attack(공격)
- **화면 절반 이상 확대**: 캐릭터 표시 높이를 항상 `화면 세로 * 0.5`로 맞춤 (`TARGET_HEIGHT_RATIO`)
- **화면 중앙 재생**: 가로는 캔버스 중앙, 세로는 고정된 바닥선(baseline)에 발이 닿도록 재생
- **5회 반복 후 1초 정지, 전체 무한 순환**: `Animation` 클래스가 반복 횟수를 세고
  다 채우면 1초간 정지한 뒤 `finished=True`가 되고, `main()`이 다음 애니메이션으로 넘어간다
  (walk → run → jump → attack → walk → ... 무한 반복)

## 보너스 항목 대응 (명시)
1. **프레임 크기가 프레임마다 달라지는 복잡한 Sprite Sheet 사용**
   `samurai_manifest.json`의 각 프레임은 고정 그리드가 아니라, 알파 채널 기준으로
   실제 그림 크기를 개별 계산한 값입니다. 예를 들어 `jump` 애니메이션은 프레임마다
   세로 크기가 아래처럼 실제로 다릅니다.
   ```
   jump 프레임 (w, h): (60,80) (62,76) (65,74) (58,80) (53,82) (53,80)
                       (51,74) (53,70) (53,74) (52,71) (51,70) (50,63)
   ```
   `Animation.__init__()`은 프레임별로 다른 (w, h)를 받아 각자 확대 비율을 계산하고,
   `Animation.draw()`는 바닥선(baseline)을 기준으로 그려서 높이가 달라도 캐릭터가
   제자리에 서 있는 것처럼 보이게 처리했습니다 (`animation_viewer.py`의 10단계 커밋 참고).

2. **애니메이션별 프레임 수가 서로 다른 경우 지원**
   walk=8, run=8, jump=12, attack=6 으로 애니메이션마다 프레임 개수가 다릅니다.
   `Animation` 클래스는 `frames` 리스트의 길이를 그대로 사용하므로 개수가 몇 개든
   동일한 코드로 동작합니다. `smoke_test.py`에서 이 사실을 자동으로 확인합니다.

## 검증
- `python smoke_test.py` : 매니페스트 속성과 반복/정지 로직을 창 없이 확인 (5개 항목 통과)
- `python animation_viewer.py` 를 직접 실행해 4개 애니메이션이 무한 순환하는 것을 화면 캡처로 확인함
