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
