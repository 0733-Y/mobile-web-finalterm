# PythonAnywhere 배포 절차 (<username> 은 본인 계정명으로 치환)

참고: https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/

## A. 웹에서 (브라우저)
1. https://www.pythonanywhere.com 가입/로그인 (무료 Beginner 계정이면 URL = `<username>.pythonanywhere.com`).
2. **Consoles → Bash** 새 콘솔 열기 (아래 B 단계 실행).
3. B 가 끝나면 **Web 탭 → Add a new web app → Next → Manual configuration → Python 3.13(없으면 3.12) → Next**.
4. Web 탭 설정:
   - Source code: `/home/<username>/mobile-web-finalterm/Service_System/Django`
   - Working directory: 같은 경로
   - Virtualenv: `/home/<username>/.virtualenvs/spacecheck`
   - Static files 표: `/static/` → `/home/<username>/mobile-web-finalterm/Service_System/Django/static`
                      `/media/`  → `/home/<username>/mobile-web-finalterm/Service_System/Django/media`
   - Code 의 **WSGI configuration file** 링크를 열어 내용을 아래 C 로 교체 후 Save.
5. 초록색 **Reload** 버튼. `https://<username>.pythonanywhere.com/admin/` 접속 확인.

## B. Bash 콘솔 (PythonAnywhere 안)
```bash
git clone https://github.com/0733-Y/mobile-web-finalterm.git
mkvirtualenv spacecheck --python=python3.13      # 3.13 이 없으면 python3.12
cd ~/mobile-web-finalterm/Service_System/Django
pip install -r requirements.txt
python -c "import secrets; print(secrets.token_urlsafe(50))"    # 출력값을 SECRET_KEY 로 사용
nano local_settings.json
```
`local_settings.json` 내용 (저장소에 올라가지 않는 파일):
```json
{"SECRET_KEY": "<위에서 출력한 값>", "DEBUG": "false",
 "ALLOWED_HOSTS": ["<username>.pythonanywhere.com"]}
```
```bash
python manage.py migrate
python manage.py seed_demo --admin-password '<직접 정한 값>' --edge-password '<직접 정한 값>'
python manage.py collectstatic --noinput
python manage.py test
```
(`seed_demo` 에 비밀번호를 주지 않으면 무작위로 만들어 `seed_credentials.json` 에 저장한다.)
비밀번호를 잊었으면 `python manage.py seed_demo --reset-passwords` (무작위 재설정, 같은 파일에 저장) 또는 `python manage.py changepassword <계정>`.
비밀번호 확인: 서버 콘솔에서 `cat seed_credentials.json` (확인 후 `clear`). 이 파일은 저장소에 올라가지 않는다.

## C. WSGI 파일 내용
```python
import os, sys
path = '/home/<username>/mobile-web-finalterm/Service_System/Django'
if path not in sys.path:
    sys.path.insert(0, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## D. 확인 (로컬 PC)
```bash
curl -s -X POST https://<username>.pythonanywhere.com/api-token-auth/ -d "username=edge" -d "password=<edge 비밀번호>"
```
`{"token": "..."}` 이 나오면 성공. Edge 는 환경변수로 접속:
`SPACECHECK_SERVER=https://<username>.pythonanywhere.com`, `SPACECHECK_PASSWORD=<edge 비밀번호>`.

## 주의
- 코드 갱신: 콘솔에서 `git pull` → (정적 파일 변경 시 `collectstatic`) → Web 탭 Reload.
- 무료 계정은 3개월마다 Web 탭에서 "Run until 3 months from today" 를 눌러 연장해야 사이트가 유지된다 (채점 끝날 때까지 서비스 유지 필요).
- 업로드 이미지는 `media/` 에 저장되며 DEBUG=false 이므로 위 `/media/` 매핑이 필수.
