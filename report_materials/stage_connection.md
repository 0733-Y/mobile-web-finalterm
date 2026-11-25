# 단계 연결 증거 — 실행 절차 (Edge → 0733 → App, 같은 Post)

목표(템플릿 v2.0): **한 번의 실행으로 만든 같은 Post**(제목에 `5960`)가 ① Edge 터미널 ② PythonAnywhere 웹 ③ App 목록에 모두 보이는 화면. 로컬 DB 복사·수동 업로드는 인정되지 않음.
비밀번호는 학생이 직접 입력한다. 이 문서와 저장소에는 비밀번호가 없다.

## 0. 준비
- 0733.pythonanywhere.com 이 SpaceCheck 로 동작 중 (`https://0733.pythonanywhere.com/` 제목이 SpaceCheck).
- edge / viewer 비밀번호: 학생이 PythonAnywhere 콘솔에서 `cat ~/mobile-web-finalterm/Service_System/Django/seed_credentials.json` 으로 확인 (확인 후 `clear`).
  - **주의 (2026-11-25)**: edge 비밀번호는 학생이 `changepassword` 로 바꿨으므로 `seed_credentials.json` 의 edge 값은 옛 값이다(로그인 안 됨). edge 는 학생이 바꾼 비밀번호를 쓴다. `seed_demo --reset-passwords` 를 실행하면 edge 도 다시 바뀌니 실행하지 말 것.
- 입력 영상: 본인 촬영 `SpaceCheck_input\selfshot_5960_540p.mp4` (저장소 밖, `Edge_System\YOLO` 기준 상대경로 `..\..\..\SpaceCheck_input\selfshot_5960_540p.mp4`).
- Edge 설정 `Edge_System\YOLO\config.json`: `space_id` 5 (시연용 공간 "스터디룸 A", 좌석 2 — 학생 동의 2026-11-25), `space_name` "스터디룸 A", `capacity` 2, `title_prefix` "5960", `min_interval_sec` 10, `mode` "count". 서버 주소·계정·비밀번호는 아래 환경변수가 덮어쓴다.
- 화면에 시계(작업 표시줄)가 보이게 둔다. 각 스크린샷에는 터미널 경로/주소창/계정/시각 중 2개 이상이 보여야 한다.

## 1. Edge (화면 ①) — PowerShell
```powershell
cd C:\Users\<사용자>\Desktop\SpaceCheck\Edge_System\YOLO
$env:SPACECHECK_SERVER = "https://0733.pythonanywhere.com"
$env:SPACECHECK_USERNAME = "edge"
$sec = Read-Host "edge password" -AsSecureString
$env:SPACECHECK_PASSWORD = [System.Net.NetworkCredential]::new("", $sec).Password
venv\Scripts\python detect.py --source ..\..\..\SpaceCheck_input\selfshot_5960_540p.mp4 --config config.json --upload --mode count --nosave 2>&1 | Select-String "UPLOAD|Error|Traceback"
```
- `Read-Host -AsSecureString` 은 입력이 `*` 로 표시된다 (그냥 `Read-Host` 는 평문으로 보이므로 쓰지 않는다).
- 기대 결과: `[UPLOAD] persons=N -> post id=<번호> level=여유` 줄이 여러 개. 참고로 같은 영상을 로컬 서버에 올렸을 때는 6줄이었다 (2026-11-24 측정). 온라인 결과 수치는 실행 후 그대로 기록할 것.
- **증거로 쓸 Post = 마지막 `[UPLOAD]` 줄의 post id** (가장 최신이라 웹·앱 목록 맨 위에 온다). 이 줄과 터미널 경로, 시계가 보이게 캡처 → `screenshots/stage_1_edge.png`.
- 끝나면 `Remove-Item Env:SPACECHECK_PASSWORD` 로 비밀번호 환경변수를 지운다.

## 2. PythonAnywhere 웹 (화면 ②)
- 브라우저에서 `https://0733.pythonanywhere.com/` → 맨 위 글이 `5960 | 스터디룸 A | N명`.
- 같은 Post 상세: `https://0733.pythonanywhere.com/post/<1단계의 post id>/` (주소창의 id 와 1단계 id 가 같음을 보이게).
- 캡처 → `screenshots/stage_2_web.png` (주소창 포함). 추가로 `/admin/` 의 Posts 목록(인원·등급 열)도 찍을 수 있음 (admin 로그인은 학생이 직접).

## 3. App (화면 ③) — 에뮬레이터
- 앱 실행 → 서버 "온라인 (0733.pythonanywhere.com)" 선택 → 아이디 `viewer`, 비밀번호 직접 입력 → 로그인.
- 목록 맨 위 = 1단계 마지막 Post (같은 제목·시각). 공간 필터를 "스터디룸 A" 로 바꿔도 맨 위에 같은 Post. 탭해서 상세(블러된 이미지) 확인.
- 이때 데이터 오래됨 띠는 초록 "최종 갱신 시각: …" 이어야 함 (업로드 직후). 10분 넘게 지난 뒤 새로고침하면 빨간 "데이터 오래됨" 으로 바뀌는 것도 F3 증거로 찍을 수 있음.
- 캡처 → `screenshots/stage_3_app.png`, `screenshots/stage_3_app_detail.png`.

## 확인 사항
- 세 화면의 제목이 모두 `5960` 으로 시작하고, 웹 주소의 id = Edge 터미널의 post id.
- 업로드는 영상 처리 중 몇 초 안에 몰려서 일어나므로 시각(분 단위)이 같을 수 있다 → 같은 Post 를 고를 때는 id 와 "목록 맨 위"를 기준으로 한다.
- 등급(좌석 2 기준, `crowd_level`): 0명 = 여유(0%), 1명 = 보통(50%), 2명 이상 = 혼잡(100%). 이 영상은 학생 1명이므로 0명/1명 Post 가 번갈아 생기며 "여유"(초록)·"보통"(노랑) 라벨이 함께 보일 것으로 예상 (실제 결과는 실행 후 기록).
- 공간 "스터디룸 A" 는 0733 과 로컬 DB 모두 id 5 (`seed_demo` 로 생성). 앱에서 공간 필터를 "스터디룸 A" 로 고르면 이 시연 Post 만 보인다.

## 실행 기록 (2026-11-25)
- 1단계(Edge, 학생 실행): 0733 에 post id=6 생성 — `5960 | 스터디룸 A | 1명`, 등급 보통. 터미널 초안 `screenshots/stage_1_edge_draft.jpg`.
- 같은 실행에서 0733 홈 화면에 스터디룸 A Post 6건 표시 확인 (2026-11-25 08:26 UTC 기준).
- 2단계(웹): `https://0733.pythonanywhere.com/post/6/` 에서 제목 `5960 | 스터디룸 A | 1명`, 보통, 2026-11-25 17:20 확인 → `screenshots/stage_2_web.png` (주소창·작업 표시줄 시계 17:38).
- 3단계(App, 학생이 viewer 로 로그인): 공간 "스터디룸 A" 필터 → 맨 위 `5960 | 스터디룸 A | 1명`, 보통, 17:20 → `screenshots/stage_3_app.png`, 상세 → `screenshots/stage_3_app_detail.png`.
  - 앱은 post id 를 표시하지 않는다. 맨 위 항목이 id 6 인 근거: 같은 공간의 최신 Post 가 웹 홈에서 `/post/6/` 이고 `/post/7/` 은 404 (2026-11-25 확인).
  - 에뮬레이터 상태바 시각은 UTC(8:36 = 한국 17:36). 보고서에 적을 때 주의.
  - 촬영 시점에 업로드 후 10분이 지나 F3 빨간 띠("데이터 오래됨 (최종 갱신 시각: 2026-11-25 17:20)")가 함께 찍힘.
- 진행 중 고친 것: 앱 상태바 아이콘이 흰 바탕에 흰색이라 시각이 안 보이던 문제(`SystemBars.setup` 에서 어두운 아이콘으로), 이미지 로드 실패를 logcat 에 남기도록(`ImageLoader`), 서버가 published_date 를 직접 기록(홈 화면 필터 문제 대응, 커밋 22e17ac).
