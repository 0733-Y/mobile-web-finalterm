# SpaceCheck — 학습 공간 혼잡도 알림

경희대 Mobile/WebService Project. 구성: `Edge_System/YOLO`(YOLOv5), `Service_System/Django`(Django+DRF, PythonAnywhere), `Client_System/Android`(Java).

## Service (로컬 실행)
```bash
cd Service_System/Django
pip install -r requirements.txt
cp local_settings.example.json local_settings.json   # SECRET_KEY 등 수정
python manage.py migrate
python manage.py seed_demo      # admin / edge 계정 + 예시 Space (비밀번호는 seed_credentials.json)
python manage.py runserver
python manage.py test
```
인증: DRF Token. `POST /api-token-auth/` → 이후 헤더 `Authorization: Token <token>`.

## 큰 파일 (저장소에 포함되지 않음)
- **YOLOv5 가중치 (`yolov5s.pt`)**: 처음 `detect.py` 실행 시 자동 다운로드되며, 수동으로는
  https://github.com/ultralytics/yolov5/releases 에서 받아 `Edge_System/YOLO/` 에 둔다.
- **입력 영상**: 본인이 촬영한 영상(`Edge_System/YOLO/` 아래, 예 `my_video.mp4`)은 저장소에 올리지 않는다. 웹캠은 `--source 0`.

## Edge 실행
```bash
cd Edge_System/YOLO
python -m venv venv && venv/Scripts/pip install -r requirements.txt   # torch 는 pytorch.org 안내대로 설치
cp config.example.json config.json
venv/Scripts/python detect.py --source 0 --config config.json --upload          # 사람 수 변화 규칙
venv/Scripts/python detect.py --source 0 --config config.json --upload --mode baseline   # 강의자료 원본 규칙(비교용)
venv/Scripts/python -m unittest test_changedetection
```

## 환경변수 (이름만)
- Django: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` (또는 `local_settings.json`, 저장소 제외)
- Edge: `SPACECHECK_SERVER`, `SPACECHECK_USERNAME`, `SPACECHECK_PASSWORD` (config.json 값을 덮어씀)
