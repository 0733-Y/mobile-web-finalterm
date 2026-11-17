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
