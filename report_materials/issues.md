# 개발 중 이슈와 해결

## 1. 강의자료의 JWT(`rest_framework_jwt`)를 쓰지 않은 이유
- `djangorestframework-jwt` 는 유지보수가 중단되어 최신 Django/DRF(여기서는 Django 5.2, DRF 3.15+)와 호환이 보장되지 않는다.
- 과제 요구는 "키(token)로 로그인"이므로 DRF 기본 `TokenAuthentication` 으로 충족된다. 추가 패키지가 없고 PythonAnywhere 배포도 단순하다.
- 변경점: 헤더가 `JWT <token>` → `Token <token>`, 발급 URL `/api-token-auth/` 은 동일. Edge·Android 모두 `Authorization: Token <token>` 사용.
- 단점: token 만료가 없다(simplejwt 와 비교). 학기말 프로젝트 범위에서는 허용하고, 필요 시 admin 에서 token 삭제로 폐기한다.

## 2. Windows 콘솔 인코딩 오류 (seed_demo)
- 한글 출력 시 `UnicodeEncodeError: 'gbk'`로 종료되어, 계정은 생성됐으나 비밀번호 저장 전에 중단됨.
- 해결: 잘못 생성된 계정을 삭제하고 `PYTHONIOENCODING=utf-8` 로 재실행.

## 3. 테스트 media 경로
- 임시 media 경로를 `/tmp/...` 로 하드코딩했던 것을 `tempfile.TemporaryDirectory` + `override_settings` 로 교체.

## 4. 영상 입력 시 최소 업로드 간격
- 증상: 비디오 파일은 실시간보다 훨씬 빠르게 처리되어, 시스템 시계로 "60초 간격"을 재면 영상 전체에서 업로드가 거의 일어나지 않을 수 있음.
- 해결: 비디오 파일 입력일 때는 영상 시간(프레임 번호 / FPS)으로 간격을 계산 (`detect.py`의 `now = frame / fps`). 웹캠은 시스템 시계 사용.
- (확인은 본인이 촬영한 영상으로 다시 해서 이 항목에 수치를 추가할 것)

## 5. 영상 처리 종료 시 Segmentation fault (2026-11-24)
- 증상: `detect.py --mode baseline` 실행 후 셸에 `Segmentation fault` 출력.
- 확인: 로그에 1856/1856 프레임과 마지막 `Speed:` 요약 줄이 모두 있고, 업로드 14건이 서버 DB 14건과 일치 → 처리 완료 후 프로세스 종료 단계에서 발생. 같은 영상의 count 모드 실행은 종료 코드 0.
- 원인: 미확인 (Windows 에서 torch/OpenCV 종료 순서 문제로 추정, 재현 조사 안 함). 측정 결과에는 영향 없음.

## 6. OpenCV 5.0 에 Haar 얼굴 검출기가 없음 (2026-11-24)
- 증상: F1 측정 스크립트에서 `AttributeError: module 'cv2' has no attribute 'CascadeClassifier'`.
- 원인: 가상환경의 opencv-python 5.0.0 에는 `CascadeClassifier` 가 포함되지 않음. 사용 가능한 검출기는 `cv2.FaceDetectorYN`(YuNet)이며 별도 ONNX 모델 파일이 필요.
- 조치: `measure_input.py` 에서 얼굴 검출기를 선택식(`--face-detector none|haar|yunet`)으로 바꾸고, 인원 수 측정은 먼저 진행. 얼굴 수 측정은 모델 파일 확보 후 진행.

## 7. 인식 단계의 흔들림 (실측, 2026-11-24, 본인 영상)
- YOLO 프레임별 사람 수가 61.87초 동안 33번 바뀌었고, 1초(30프레임) 미만으로 유지된 구간이 22개 (`measurements/2026-11-24/summary_none.json`).
- 같은 영상에서 강의자료 원본 규칙은 Post 14건, 사람 수 변화 규칙은 1건 (`measurements/2026-11-24/README.md`). 원본 규칙의 Post 는 인식 단계의 흔들림(검출이 1~3프레임 끊김)에 그대로 반응한 것이 포함됨 → 인식 오류이며 규칙 오류와 구분해서 기록.
