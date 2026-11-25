# AI(Claude Code) 사용 기록

도구: Claude Code. 아래는 파일별로 누가 썼는지 기록한다. (구두 확인에서 AI 작성 코드도 본인 코드로 취급되므로, 각 파일의 핵심 동작을 이해하고 있어야 함)

| 파일 | 작성 | 비고 |
|---|---|---|
| Edge_System/YOLO/* (utils, models 등) | 외부 원본 | ultralytics/yolov5, 수정 없음 |
| Edge_System/YOLO/detect.py | 원본 + AI 수정 | SpaceCheck 주석이 달린 부분이 AI 수정 (person 한정, ChangeDetection 호출, 옵션 추가) |
| Edge_System/YOLO/changedetection.py | AI | 변화 감지, 업로드, 블러, 제목 접두어, baseline 모드 |
| Edge_System/YOLO/test_changedetection.py, post_test.py | AI | |
| Edge_System/YOLO/measure_input.py | AI | 필요성·F1 측정용. 측정 실행과 수치 기록은 AI, 영상 내용 확인(실제 1명, laptop 없음)은 학생 |
| Service_System/Django/blog/*, config/* | AI | 모델·API·admin·테스트·seed 명령, 권한 클래스(permissions.py, 학생이 viewer 읽기 전용 결정) |
| Client_System/Android/* | AI | 로그인·목록·상세·공간 필터·데이터 오래됨 안내. 학생 결정: N=10분, 화면 문구 한국어, 서버 주소 전환 방식 |
| report_materials/* | AI 작성 초안 | |

학생이 결정한 것 (AI 는 제안·구현):
- 인증 방식 DRF Token, viewer 읽기 전용 권한, 최소 업로드 간격 60초 → 10초, 데이터 오래됨 N=10분
- 자유 기능 F1 개인정보 블러 / F2 혼잡 상태 / F3 데이터 오래됨 안내 (즐겨찾기·알림은 하지 않기로 결정)
- 0733 계정을 SpaceCheck 로 전환, YOLOv5 원본 단독 커밋을 위한 이력 재작성, 커밋 서명 줄 제거
- 입력 영상 촬영(본인), 영상 내용 판정(중복 검출·오검출 확인)

AI 가 정리한 보고서 자료: `report_materials/checklist.md` 의 F1~F3 절(측정 파일의 실측값만 사용), `issues.md`, `stage_connection.md`, `measurements/*/README.md`.

검증 방법: Django `manage.py test`, Edge `unittest`, 로컬 서버에 실제 업로드 후 DB/이미지 확인.
학생 본인 수정 내용: (본인이 직접 채울 것)
