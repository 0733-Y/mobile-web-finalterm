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
- 조치: `measure_input.py` 에서 얼굴 검출기를 선택식(`--face-detector none|haar|yunet`)으로 바꾸고, 학생 동의 후 YuNet 모델(opencv_zoo)을 받아 측정. 결과: 블러 전 59 → 블러 후 0.

## 7. 인식 단계의 흔들림 (실측, 2026-11-24, 본인 영상)
- YOLO 프레임별 사람 수가 61.87초 동안 33번 바뀌었고, 1초(30프레임) 미만으로 유지된 구간이 22개 (`measurements/2026-11-24/summary_none.json`).
- 같은 영상에서 강의자료 원본 규칙은 Post 14건, 사람 수 변화 규칙은 1건 (`measurements/2026-11-24/README.md`). 원본 규칙의 Post 는 인식 단계의 흔들림(검출이 1~3프레임 끊김)에 그대로 반응한 것이 포함됨 → 인식 오류이며 규칙 오류와 구분해서 기록.

## 8. 인식 오류 사례 (학생이 영상으로 확인, 2026-11-24)
- **중복 검출**: 영상에는 처음부터 끝까지 학생 1명뿐인데, YOLO 가 11프레임에서 2명으로 검출. → count 모드에서는 30프레임 안정 조건 때문에 업로드로 이어지지 않음 (2명 구간이 30프레임 미만).
- **오검출(laptop)**: 화면에 노트북이 없는데 4프레임에서 laptop 으로 검출. → baseline(80클래스) 모드에서 Post 1건(`5960 | laptop`) 생성. count 모드는 person 만 보므로 영향 없음.
- 두 사례 모두 인식 단계(YOLO) 오류이며, 판정 규칙 오류가 아님.

## 9. 얼굴 검출기의 한계 (F1 측정, 2026-11-24)
- 학생이 마스크를 착용해 YuNet 이 사람 있는 660프레임 중 59프레임에서만 얼굴을 찾음. 블러 후 0건이지만, 검출기가 못 찾은 얼굴이 가려졌는지는 이 수치로 확인할 수 없음. 임계값을 낮춰 수치를 맞추지 않음.

## 10. 평가용 viewer 계정을 읽기 전용으로 만든 이유 (권한 설계, 2026-11-25 학생 결정)
- 문제: 처음 설계는 "로그인한 계정이면 누구나 POST 가능"(`IsAuthenticated`). 제출물 `url.txt` 에 평가용 계정 비밀번호를 적어야 하는데, 그 계정으로 Post 를 올리거나 지울 수 있으면 서비스 데이터(공간별 최신 인원)가 오염될 수 있다.
- 결정: 쓰기(POST/PUT/PATCH/DELETE)는 `blog.add_post` 권한이 있는 계정만 허용. 권한은 Edge 업로드용 `edge` 계정(과 관리자)에만 부여하고, `viewer` 는 조회(GET)만 가능.
- 구현: `Service_System/Django/blog/permissions.py` `IsUploaderOrReadOnly`, `blog/views.py` `BlogImages.permission_classes`, 권한 부여는 `blog/management/commands/seed_demo.py` (`Command.handle`).
- 확인: 테스트 `blog/tests.py` `test_viewer_read_only`(viewer GET 200, POST 403), `test_viewer_cannot_delete`(DELETE 403) 포함 7건 통과(로컬·PythonAnywhere 모두). 서버에서 `has_perm('blog.add_post')`: admin True, edge True, viewer False.
- 영향: App 은 읽기만 하므로(로그인 토큰 발급 `/api-token-auth/` 는 권한과 무관) 변경 없음. Edge 는 edge 계정을 쓰므로 그대로 업로드 가능.
- 비밀번호: viewer 비밀번호는 서버의 git 제외 파일 `seed_credentials.json` 에만 있고, 저장소의 `url.txt` 에는 쓰지 않음(제출 압축파일 쪽에만 학생이 기재).

## 11. Android 17(API 37) 에서 에뮬레이터 → 로컬 서버(10.0.2.2) 연결 실패 (2026-11-25)
- 증상: 로그인 시 "서버에 연결할 수 없습니다". 서버 로그에는 요청이 오지 않음. logcat: `SocketTimeoutException: failed to connect to /10.0.2.2 (port 8000) ... after 15000ms`.
- 원인 확인: 에뮬레이터 셸에서는 `nc 10.0.2.2 8000` 으로 서버에 접속되고 응답(401)도 옴 → 네트워크 문제가 아니라 앱 단위 제한. API 37 SDK 에 런타임 권한 `android.permission.ACCESS_LOCAL_NETWORK` 가 있고(위험 권한), 앱에 없었음 → 사설 IP 접속이 막힘.
- 해결: Manifest 에 권한 선언, 로그인 때 "에뮬레이터 로컬" 서버를 고른 경우에만 런타임 요청 (`LoginActivity.needsLocalNetworkPermission`, `onRequestPermissionsResult`). 온라인(https) 서버는 권한 불필요.
- 확인: 권한 허용 후 같은 요청이 서버에 도착(400/200), 로그인·목록 정상.
- 실패 단계: 표시/연결 단계 (YOLO 인식·판정 규칙과 무관).

## 12. Android 15+ edge-to-edge 로 화면 위쪽이 액션바에 가려짐 (2026-11-25)
- 증상: 로그인 화면 제목과 "서버" 라벨이 액션바 뒤에 겹쳐 보이지 않음.
- 원인: targetSdk 37 에서는 화면이 상태바·액션바 아래까지 그려짐.
- 해결: NoActionBar 테마 + 각 레이아웃에 MaterialToolbar, 루트 뷰에 시스템 바 크기만큼 패딩 (`SystemBars.setup`).
- 확인: 에뮬레이터 스크린샷에서 툴바 아래에 제목·입력칸이 정상 표시.

## 13. 시연 녹화 중 터미널 한글 깨짐 (2026-11-25)
- 증상: `detect.py ... | Select-String` 출력에서 level(여유/보통)이 깨진 글자로 표시.
- 원인: Windows PowerShell 5.1 이 파이프로 받은 Python 의 UTF-8 출력을 콘솔 기본 코드페이지(GBK)로 해석.
- 해결: 실행 전 `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`, `$env:PYTHONIOENCODING = "utf-8"`.
- 확인: 2차 녹화(`demo/demo.mp4`)에서 `level=여유/보통` 정상 표시. (실패 단계: 표시 — 서버 데이터는 정상)

## 14. 앱 메뉴 글자가 보이지 않음 (2026-11-25)
- 증상: 목록 화면 ⋮ 메뉴(새로고침/로그아웃)가 흰 바탕에 흰 글자.
- 원인: 툴바에 어두운 테마 오버레이를 줘서 팝업 메뉴도 흰 글자를 상속.
- 해결: 세 레이아웃의 MaterialToolbar 에 `app:popupTheme="@style/ThemeOverlay.MaterialComponents.Light"`.
- 확인: 에뮬레이터에서 "새로고침", "로그아웃" 이 검은 글자로 보임.
