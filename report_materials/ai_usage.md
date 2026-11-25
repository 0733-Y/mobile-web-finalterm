# AI(Claude Code) 사용 기록

도구: Claude Code. 아래는 파일별로 누가 썼는지 기록한다. (구두 확인에서 AI 작성 코드도 본인 코드로 취급되므로, 각 파일의 핵심 동작을 이해하고 있어야 함)

| 파일 | 작성 | 비고 |
|---|---|---|
| Edge_System/YOLO/* (utils, models 등) | 외부 원본 | ultralytics/yolov5, 수정 없음 |
| Edge_System/YOLO/detect.py | 원본 + AI 수정 | SpaceCheck 주석이 달린 부분이 AI 수정 (person 한정, ChangeDetection 호출, 옵션 추가) |
| Edge_System/YOLO/changedetection.py | AI | 변화 감지, 업로드, 블러, 제목 접두어, baseline 모드 |
| Edge_System/YOLO/test_changedetection.py, post_test.py | AI | |
| Service_System/Django/blog/*, config/* | AI | 모델·API·admin·테스트·seed 명령, 권한 클래스(permissions.py, 학생이 viewer 읽기 전용 결정) |
| report_materials/* | AI 작성 초안 | |

검증 방법: Django `manage.py test`, Edge `unittest`, 로컬 서버에 실제 업로드 후 DB/이미지 확인.
학생 본인 수정 내용: (본인이 직접 채울 것)
