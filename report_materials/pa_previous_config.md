# PythonAnywhere 기존 웹앱(PhotoBlog) 설정 백업 — 2026-11-17, SpaceCheck 로 교체하기 전

되돌리려면 Web 탭에서 아래 값으로 복원하고 WSGI 파일을 아래 내용으로 되돌린 뒤 Reload.

- 웹앱: 0733.pythonanywhere.com (Python 3.12)
- Source code: `/home/0733/PhotoBlog/PhotoBlogServer`
- Working directory: `/home/0733/`
- Virtualenv: `/home/0733/.virtualenvs/photoblog`
- Static files: `/static/` → `/home/0733/PhotoBlog/PhotoBlogServer/staticfiles`
               `/media/`  → `/home/0733/PhotoBlog/PhotoBlogServer/media`
- Force HTTPS: Disabled (교체 후 http 요청이 리다이렉트 없이 200 으로 응답하는 것으로 확인. 처음 백업에 Enabled 라고 적은 것은 페이지 문구를 잘못 읽은 것)
- 만료 예정일(당시): 2026-11-27
- 교체 후: 소스 `/home/0733/mobile-web-finalterm/Service_System/Django`, venv `/home/0733/.virtualenvs/spacecheck`, 정적 `/static/`, `/media/` 매핑은 SpaceCheck 경로로 변경됨. 기존 PhotoBlog 코드·venv 는 디스크에 그대로 남아 있음.

WSGI 파일 `/var/www/0733_pythonanywhere_com_wsgi.py` 원래 내용 (참고: Web 탭의 Source/venv 값과 달리 실제로는 아래 경로를 사용하고 있었음):
```python
import os
import sys

project = '/home/0733/MobileWebService-Common-Eval02/PhotoBlogServer'
site = '/home/0733/.virtualenvs/venv/lib/python3.12/site-packages'
for p in (project, site):
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 2026-11-17 PhotoBlog 복원 기록 (공통평가 02 평가용 사이트를 되돌림)
- 위 "원래 설정"대로 WSGI 파일, Source code, Virtualenv, `/static/`·`/media/` 매핑을 복원하고 Reload 함. Force HTTPS 는 건드리지 않아 비활성 그대로.
- 확인: 홈 "Intruder Detection" 게시글 37개(id 1~37) 표시, 이미지 37/37 로드, `/api_root/Post/` 200 (37건), 상세 200, 가장 오래된 이미지 200 image/jpeg, `/admin/login/` 200, 정적 파일 200.
- 0733 계정은 이후 변경하지 않는다. `spacecheck` virtualenv 와 `~/mobile-web-finalterm` 코드는 삭제하지 않고 디스크에 남겨 둠 (웹앱과 연결되어 있지 않음).
- SpaceCheck 는 로컬에서 계속 개발하고, 공통평가 02 평가가 끝났다는 학생의 확인 후에 0733 으로 다시 배포한다 (그 전에는 0733 설정을 바꾸지 않는다). 재배포할 때는 이 문서의 "교체 후" 값을 참고.
