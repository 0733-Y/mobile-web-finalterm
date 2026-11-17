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
- **데모 영상 (`Edge_System/YOLO/demo.mp4`)**: 100MB 제한과 라이선스 때문에 저장소에 없다.
  Mixkit 무료 소스(https://mixkit.co/free-stock-video/library/)에서 고정 카메라로 사람이 드나드는
  도서관/자습실 영상(20초~1분)을 받아 `demo.mp4` 로 저장한다. 출처·라이선스는 `report_materials/urls.md` 참고.
