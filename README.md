# Drill #11 · 소년 AutoRun

2D 게임프로그래밍 실습 과제. `PRD.md`의 요구사항을 기준으로 단계별로 개발한다.

## 실행

Python 3.13에서 검증한다. 저장소 폴더에서 다음 명령을 실행한다.

```powershell
python -m pip install -r requirements.txt
python main.py
```

실행 진입점은 `main.py`다. 이미지는 소스 파일 위치를 기준으로 로드하므로
다른 폴더에서 `main.py`의 전체 경로를 지정해 실행해도 된다.

## 기본 조작

| 키 | 동작 |
| --- | --- |
| 왼쪽 / 오른쪽 | 해당 방향으로 일반 달리기 |
| 방향키 해제 또는 양쪽 동시 입력 | 일반 달리기 정지 |
| Space | Sleep에서 Idle로 복귀 |
| Escape / 창 닫기 | 종료 |

Idle 상태에서 5초 대기하면 Sleep으로 전환된다. Sleep에서도 방향키로 달릴 수 있다.

## 검사

```powershell
python -m unittest discover -s tests -v
```

이미지는 수업 실습에 제공된 `animation_sheet.png`, `grass.png`를 사용한다.
