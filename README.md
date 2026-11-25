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
권한: 조회(GET)는 로그인한 모든 계정, 업로드·수정·삭제는 `blog.add_post` 권한이 있는 `edge` 계정만. `seed_demo` 가 admin / edge / viewer(읽기 전용) 계정을 만든다.

## Client (Android, Java)
```bash
cd Client_System/Android
# local.properties 에 sdk.dir 지정 (저장소 제외). JDK 17+ (Android Studio 의 jbr 사용 가능)
./gradlew assembleDebug testDebugUnitTest
adb install -r app/build/outputs/apk/debug/app-debug.apk
```
- 로그인 화면에서 서버 선택: 온라인 `https://0733.pythonanywhere.com` / 에뮬레이터 로컬 `http://10.0.2.2:8000` (PC 에서 `python manage.py runserver` 필요).
- 아이디·비밀번호는 실행 중 입력. 비밀번호와 토큰은 코드·저장소에 없음 (토큰은 기기의 SharedPreferences 에만 저장).
- Android 17(API 37) 에서 로컬 서버를 고르면 "근처 기기(로컬 네트워크)" 권한을 요청한다.

## 큰 파일 (저장소에 포함되지 않음)
- **YOLOv5 가중치 (`yolov5s.pt`)**: 처음 `detect.py` 실행 시 자동 다운로드되며, 수동으로는
  https://github.com/ultralytics/yolov5/releases 에서 받아 `Edge_System/YOLO/` 에 둔다.
- **입력 영상**: 본인이 촬영한 영상(`Edge_System/YOLO/` 아래, 예 `my_video.mp4`)은 저장소에 올리지 않는다. 웹캠은 `--source 0`.

## F1 측정용 얼굴 검출 모델 (저장소에 포함되지 않음)
`Edge_System/YOLO/face_model/face_detection_yunet_2023mar.onnx` (232,589 바이트) — opencv_zoo 에서 받는다:
```bash
cd Edge_System/YOLO && mkdir -p face_model
curl -L -o face_model/face_detection_yunet_2023mar.onnx https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
venv/Scripts/python measure_input.py --source <본인 영상> --out <결과 폴더> --face-detector yunet --face-model face_model/face_detection_yunet_2023mar.onnx
```

## 외부 코드 출처
- `Edge_System/YOLO/` 의 기반: [ultralytics/yolov5](https://github.com/ultralytics/yolov5) 버전 7.0.0 (pyproject.toml), 커밋 `1e7cf74cb64d719b34f7315aa13eab9e32cde672` (2026-11-17). 라이선스 AGPL-3.0.
- 최초 임포트 커밋(`215ce63`)은 원본 그대로이며, 수정은 이후 커밋에서만 이루어졌다(`detect.py` 수정, `changedetection.py` 등 추가).

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
