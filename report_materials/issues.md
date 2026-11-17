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

## 4. 데모 영상 선정과 연속 프레임 수
- 보통 YOLOv5s 는 사람이 겹치거나 일부 가려지면 프레임마다 검출 수가 1씩 흔들린다. 후보 영상 16개(Mixkit)를 같은 규칙으로 돌려 보니, 사람이 많은 장면(사무실/카페)은 인원이 계속 흔들려 "N프레임 연속 유지" 조건을 거의 만족하지 못했다.
- 선택한 영상(ID 48162)은 인원이 0→1→3→4 로 변하지만, 규칙의 기본값인 30프레임에서는 일부 단계(1명, 3명)가 연속 30프레임을 채우지 못해 업로드가 2회뿐이었다.
- 대응: 코드 기본값(30)은 유지하고, 데모 실행 때만 `--stable-frames 20`(25fps 기준 약 0.8초), `--min-interval 2`로 덮어써서 4회 업로드를 확인. 실제 운영(카메라 30fps, 최소 간격 60초)과 다른 설정이므로 보고서에 명시한다.
- 비디오 파일은 실시간보다 훨씬 빨리 처리되므로, 최소 업로드 간격은 시스템 시계가 아니라 영상 시간(프레임 번호/FPS)으로 계산한다.
