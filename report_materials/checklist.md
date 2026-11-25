# 조건 대비표 체크리스트 (진행 중)

자유 기능: F1 개인정보 블러, F2 혼잡 상태, F3 데이터 오래됨 안내 (아래 "자유 기능 F1~F3" 절)

| 번호 | 구현(O/X) | 대체(O/X) | 파일 / 함수·클래스 | 설명 |
|---|---|---|---|---|
| 1-1 | O | X | Edge_System/YOLO/detect.py `run()` | YOLOv5s 사전학습 모델 사용 (yolov5s.pt, 첫 실행 시 자동 다운로드) |
| 1-2 | O | O | detect.py `parse_opt()` (`opt.classes=[0]`) | COCO 80클래스 중 person 만 검출 — 대체 |
| 1-3 | O | O | Edge_System/YOLO/changedetection.py `ChangeDetection.update/mark_uploaded`; detect.py `run()` | 물체 유무 대신 사람 수 변화(연속 N프레임 유지)로 변경 감지 — 대체 |
| 1-4 | O | X | changedetection.py `ChangeDetection.get_token`, `ChangeDetection.upload` | token 인증 후 `/api_root/Post/` 로 multipart POST |
| 1-5 | O | X | changedetection.py `blur_boxes`, `crowd_level`; detect.py (`--upload`, `--config`) | 사람 영역 블러(개인정보), 혼잡도 등급 계산, 비디오 파일 입력 지원, 제목에 5960 접두어(`make_title`), 강의자료 ch08 원본 규칙 모드(`--mode baseline`: `ChangeDetection.update_baseline/upload_baseline`, detect.py 80클래스 각각 result_prev, 0→1 즉시 업로드, 320x240, 제목=클래스명(앞에 5960), 본문=새 클래스명 쉼표 연결) |
| 3-1 | O | X | Client_System/Android/app/src/main/java/kr/ac/khu/spacecheck/PostListActivity.java `PostListActivity`, PostAdapter.java `PostAdapter` (+ res/layout/item_post.xml) | Post 목록(RecyclerView): 썸네일, 제목, 인원·공간, 혼잡도 색 라벨(여유 초록/보통 노랑/혼잡 빨강), 시각. 최신순, 당겨서 새로고침, 끝까지 스크롤 시 다음 페이지 |
| 3-2 | O | X | Client_System/Android/app/src/main/java/kr/ac/khu/spacecheck/net/SpaceCheckApi.java `SpaceCheckApi.posts/postsPage/post/spaces`, net/ApiClient.java `ApiClient.create` | Retrofit 으로 목록·상세 GET, 헤더 `Authorization: Token <token>`. 상세 화면 PostDetailActivity.java `PostDetailActivity` |
| 3-3 | O | X | LoginActivity.java `LoginActivity`, PostListActivity.java `setupSpinner`, PostDetailActivity.java | 시나리오: 로그인(서버 선택) → 공간별 필터 → 목록 → 상세. 401 이면 로그인 화면으로 |
| 3-4 | O | X | StaleChecker.java `StaleChecker.isStale`, PostListActivity.java `updateStaleBanner` | 데이터 오래됨 안내: 최종 갱신이 10분(학생 결정 N=10) 초과면 "데이터 오래됨 (최종 갱신 시각: …)" 빨간 띠, 10분 이내면 초록 "최종 갱신 시각", 데이터 없으면 회색 |
| 2-1 | O | X | Service_System/Django/config/settings.py (REST_FRAMEWORK: TokenAuthentication), config/urls.py (`obtain_auth_token`), blog/permissions.py `IsUploaderOrReadOnly` | DRF Token 인증(`Authorization: Token <token>`, `/api-token-auth/`). 쓰기는 `blog.add_post` 권한 계정(edge)만, 평가용 viewer 는 읽기 전용 (이유: issues.md 10) |
| 2-2 | O | X | blog/models.py `Post`, `Space`; blog/admin.py `PostAdmin`, `SpaceAdmin`; blog/views.py `post_list`, `post_detail` | 이미지 블로그 + Django admin |
| 2-3 | O | X | blog/views.py `BlogImages` (POST `/api_root/Post/`), `perform_create` | Edge 업로드용 |
| 2-4 | O | X | blog/views.py `BlogImages` (GET 목록/상세), `SpaceViewSet` (`/api_root/Space/`) | 최신순, 페이지네이션, `?space=` 필터 |
| 2-5 | O | X | blog/serializers.py `SpaceSerializer.get_latest`; blog/tests.py `ApiTests` | 공간별 최신 상태, 자동 테스트 5건 통과 (Django 5.2 LTS) |

(1-x, 3-x, PythonAnywhere 배포는 이후 단계에서 추가)

## 예시 데이터 안내
`python manage.py seed_demo` (blog/management/commands/seed_demo.py)가 만드는 Space 5개(좌석 수 120/80/30/50, 그리고 단계 연결 시연용 "스터디룸 A" 2석 — 학생 동의 2026-11-25)는 **데모용 임의 예시 데이터**이며 실제 시설 정보가 아니다.

## 자유 기능 F1~F3 (학생 결정 2026-11-25)
F1 개인정보 블러 / F2 혼잡 상태 / F3 데이터 오래됨 안내. (즐겨찾기·알림은 하지 않음 — 학생 결정)
조건 대비표와의 대응: F1 → 1-5, F2 → 1-5·2-5·3-1 라벨, F3 → 3-4.
행 번호는 커밋 `338e349` 기준. 수치는 모두 실측값이며, 측정하지 않은 항목은 "미측정"으로 적는다.
측정 자료: `report_materials/measurements/2026-11-24/` (본인 촬영 `selfshot_5960_540p.mp4`, 1856프레임, 30fps, 61.87초).

### F1 개인정보 블러 (Edge)
- **문제 정의**: Edge 가 올리는 스냅샷에 사람 얼굴이 그대로 남으면 공개 서비스에서 누가 공부하는지 알아볼 수 있다. 실측: 같은 영상에서 원본 프레임 기준으로 얼굴 검출기(YuNet)가 얼굴을 찾은 프레임 59개.
- **설계 이유**: YOLO 가 이미 찾은 사람 박스 전체를 가우시안 블러(커널 51). 버린 안: (1) 얼굴 검출 후 얼굴만 블러 — 실측에서 사람이 있는 660프레임 중 얼굴이 검출된 것은 59프레임뿐(마스크 착용)이라 대부분 놓친다. (2) 이미지 전체 블러 — 좌석·공간 상태까지 안 보여서 사진의 의미가 없어진다.
- **구현 위치**: `Edge_System/YOLO/changedetection.py` `blur_boxes` (45–52행); 호출 `Edge_System/YOLO/detect.py` 326–329행 (`cd.update` 가 True 일 때 원본 프레임 `raw0` 를 블러한 뒤 `cd.upload`). 끄기 옵션 `--no-blur`.
- **강의자료 코드와의 차이**: 강의자료 원본 규칙(본 프로젝트의 `--mode baseline` 재현, `upload_baseline`)은 프레임을 320x240 으로 줄여 그대로 올린다(블러 없음). F1 은 원본 해상도에서 사람 영역만 블러한다.
- **전후 비교 (같은 영상, 같은 검출기 YuNet score 0.9, 1856프레임 전부)**: 얼굴 검출 수 59 → 0, 얼굴이 검출된 프레임 59 → 0. (`summary_yunet.json`)
- **정상 사례**: 사람이 검출된 프레임 → 박스 영역이 블러되어 업로드됨. count 모드 Post 6건 중 1명 Post 3건은 사람 영역이 블러된 이미지(앱 목록 썸네일과 상세 화면 1건에서 확인), 0명 Post 3건은 블러할 사람이 없음.
- **예외 사례**: YOLO 가 사람을 놓친 프레임은 블러되지 않는다. 이번 영상에서는 "얼굴은 검출됐는데 사람은 검출되지 않은 프레임" 0개로, 실제 발생은 관찰되지 않음. baseline 모드는 비교용이라 블러하지 않는다.
- **한계**: 마스크 때문에 원본 얼굴 검출 자체가 59/660 프레임으로 적어, "블러 후 0"은 검출기가 찾을 수 있던 얼굴이 사라졌다는 뜻이지 모든 얼굴이 가려졌다는 증명은 아니다. 블러 강도가 충분한지에 대한 사람 눈 평가는 미측정.

### F2 혼잡 상태 (Edge + Service + App)
- **문제 정의**: 이미지와 제목만으로는 자리가 얼마나 남았는지 알 수 없다. 실측: 같은 영상을 강의자료 원본 규칙으로 돌리면 Post 14건이 생기지만, 14건 모두 인원 수·공간·등급 정보가 없다(앱에서 "0명 · 공간 미지정 · 등급 없음"으로 표시됨).
- **설계 이유**: 판정은 명확한 규칙으로 — 인원/좌석 수 < 40% 여유, 40~80% 보통, ≥ 80% 혼잡 (임계값은 Claude 제안, 학생 동의). Edge 에서 계산해 Post 에 `person_count`·`level` 을 함께 올리고, 서버는 공간별 최신 상태를 모아 주며, 앱은 색 라벨로 보여 준다. 버린 안: 서버에서 등급 계산 — 좌석 수를 아는 Edge 설정과 서버 `Space.capacity` 가 이중 관리됨 (현재도 이중 관리 위험은 한계로 남음).
- **구현 위치**: Edge `changedetection.py` `crowd_level` (35–42행), `ChangeDetection.upload` 103행(`level` 필드); Service `blog/models.py` `Space`(6행~, `capacity` 11행), `Post.person_count`/`level` (38–39행), `blog/serializers.py` `SpaceSerializer.get_latest` (24행~), `blog/views.py` `SpaceViewSet` (39행~); App `LevelStyle.color` (10–15행), `PostAdapter.bindLevel` (77–83행).
- **강의자료 코드와의 차이**: 강의자료 Post 는 title/text/image/날짜뿐이고 공간·인원·등급 개념이 없다.
- **전후 비교 (같은 영상)**: 강의자료 원본 규칙 Post 14건 중 인원·등급 있는 Post 0건 → 사람 수 변화 규칙(F2 포함) Post 6건 중 6건에 인원·등급 포함. 사용자가 상태를 알아내는 데 걸리는 시간 비교는 미측정.
- **정상 사례**: count 모드 Post 6건 → 앱 목록에 "0명/1명 · 중앙도서관 제1열람실", 초록 "여유" 라벨. 단위 테스트 `test_changedetection.py` `test_level`: 좌석 10석에서 3명 여유, 4명 보통, 7명 보통, 8명 혼잡 (통과).
- **예외 사례**: 공간이 없는 Post(baseline) → "공간 미지정", 회색 "등급 없음".
- **한계**: 등급은 `capacity` 값에 전적으로 의존한다. 이번 측정은 config 의 capacity=120 이어서 1명(0.8%)도 모두 "여유"였다 — 좌석 수를 잘못 등록하면 등급이 틀린다(ch14 위험 요소). 또 YOLO 인원 오차(실측: 혼자인데 2명으로 센 프레임 11개)가 등급에 그대로 반영될 수 있다(30프레임 안정 조건으로 이번 영상에서는 업로드까지 가지 않음).

### F3 데이터 오래됨 안내 (App)
- **문제 정의**: Edge 가 멈춰도 앱 목록은 마지막 Post 를 계속 보여 주므로, 오래된 상태를 현재 상태로 오해할 수 있다. 실측: 2026-11-25 15:30 에 앱을 열었을 때 최신 데이터는 2026-11-24 13:00 (약 26.5시간 전). 목록의 각 줄에는 시각만 있어서 이 차이를 사용자가 직접 계산해야 한다.
- **설계 이유**: 목록은 최신순이므로 맨 위 Post 의 시각 = 현재 필터(전체/공간)의 최종 갱신 시각. 지금과의 차이가 N=10분(학생 결정, Edge 최소 업로드 간격 10초보다 충분히 김)을 넘으면 빨간 띠 "데이터 오래됨 (최종 갱신 시각: …)". 버린 안: 서버에서 판정 — 앱이 보는 시각 기준이 더 직관적이고 서버 변경이 필요 없음. 줄마다 표시 — 화면이 복잡해짐.
- **구현 위치**: App `StaleChecker.isStale` (17–20행), `PostListActivity.updateStaleBanner` (201–216행, 목록을 받을 때와 `onResume` 에서 호출).
- **강의자료 코드와의 차이**: 강의자료(공통 평가) 앱 목록은 Post 를 보여 주기만 하고 데이터의 신선도를 판정하지 않는다.
- **전후 비교 (같은 데이터, 같은 시각)**: 적용 전(띠 없는 목록) — 경고 없음, 각 줄의 시각만 표시 (적용 전 화면은 따로 캡처하지 않음. 보고서용 비교 화면이 필요하면 띠를 끈 빌드로 찍어야 함). 적용 후 — 빨간 띠 "데이터 오래됨 (최종 갱신 시각: 2026-11-24 13:00)" (에뮬레이터 확인). 오인 감소 효과의 사용자 측정은 미측정.
- **정상 사례**: 방금 만든 Post → 초록 "최종 갱신 시각: 2026-11-25 15:30" (에뮬레이터 확인).
- **예외 사례**: 10분 초과 → 빨간 띠 (11/24 데이터, 에뮬레이터 확인). 데이터 없는 공간 → 회색 "아직 데이터가 없습니다." (공학관 스터디룸, 에뮬레이터 확인). 단위 테스트 `StaleCheckerTest` 4건: 9분·정확히 10분은 오래되지 않음, 10분 1초·3시간은 오래됨, 시각 없음은 오래됨 (통과).
- **한계**: 기기 시계가 틀리면 판정도 틀린다. 앱을 켜 둔 채로는 자동 재판정하지 않고, 새로고침이나 화면 복귀 때만 다시 계산한다. "Edge 가 멈춤"과 "사람 수가 안 변해서 업로드가 없음"을 구분하지 못한다(인원이 그대로면 Edge 는 올리지 않음).

## 필요성 측정 계획 (본인 촬영 영상 도착 후)
같은 영상으로 두 모드를 각각 실행하고 "X초 동안 Y개 Post" 를 기록 (서버 Post 목록에서 개수 확인):
```bash
venv/Scripts/python detect.py --source my_video.mp4 --config config.json --upload --mode baseline
venv/Scripts/python detect.py --source my_video.mp4 --config config.json --upload --mode count
```

## 필요성 측정 결과 (2026-11-24, 본인 촬영 영상 61.87초)
- 강의자료 원본(`--mode baseline`): Post 14건 / 사람 수 변화(`--mode count`, 30프레임+60초): Post 1건.
- YOLO 프레임별 사람 수 변화 33회, 1초 미만 구간 22개.
- F1 블러 전후 얼굴 수(YuNet): 59 → 0 (마스크 착용으로 원본 검출 자체가 적음).
- 최소 간격 10초로 변경 후(학생 동의): baseline 14건 / count 6건.
- 상세: `report_materials/measurements/2026-11-24/README.md`, 측정 스크립트 `Edge_System/YOLO/measure_input.py`

## App 테스트 기록 (2026-11-25, Pixel_7 에뮬레이터 API 37, 로컬 서버 10.0.2.2:8000)
| 기능 | 정상 | 규칙 위반 / 예외 | 정보 부족 |
|---|---|---|---|
| 로그인 | viewer 계정 로그인 → 목록 화면 | 틀린 비밀번호 → 서버 400 → "아이디 또는 비밀번호가 올바르지 않습니다." | 아이디 빈칸 → "아이디와 비밀번호를 입력하세요." (요청 안 보냄) |
| 목록·상세 | 35건 최신순, 썸네일(블러된 이미지) 로드, 상세 화면 이미지·등급·인원 표시 | 공간 없는 baseline Post → "공간 미지정", "등급 없음" 회색 | - |
| 공간 필터 | 제2열람실 → `?space=2` 요청, 1건 | - | 공학관 스터디룸 → `?space=3` 0건 → "게시글이 없습니다." |
| 데이터 오래됨(N=10) | 방금 만든 Post → 초록 "최종 갱신 시각: 2026-11-25 15:30" | 전날(11/24 13:00) 데이터 → 빨강 "데이터 오래됨 (최종 갱신 시각: 2026-11-24 13:00)" | Post 없는 공간 → 회색 "아직 데이터가 없습니다." |
- 단위 테스트: `Client_System/Android/app/src/test/.../StaleCheckerTest.java` 4건 통과 (10분 이내/정확히 10분/10분 1초 초과/시각 없음).
- 오래됨 테스트용 Post 1건(제2열람실, "앱 테스트")은 로컬 DB 에 임시로 만들었다가 삭제함. 온라인(0733) 서버로의 App 동작은 아직 확인하지 않음.

## 스크린샷 목록 (2026-11-25 촬영, `report_materials/screenshots/`, 저장소 제외)
보이는 증거 항목: 주소창 / 터미널 경로 / 계정 / 시각 (2개 이상). 비밀번호·PythonAnywhere 콘솔 내용은 없음.
| 상태 | 파일 | 내용 | 보이는 증거 항목 |
|---|---|---|---|
| ✅ | `git_log.png` | `git log --date=short --format="%h %ad %s"` | 터미널 경로, 작업 표시줄 시각 (모든 커밋 후 마지막 촬영) |
| ✅ | `1-3_count_mode.png` | 0733 업로드 count 모드: `[UPLOAD]` 6줄(post id 13~18), 브라우저 0733 홈 | 터미널 경로, 주소창, 시각 |
| ✅ | `need_count.png` | 필요성: 사람 수 규칙 6건 (위와 같은 화면) | 터미널 경로, 주소창, 시각 |
| ✅ | `need_baseline.png` | 필요성: 강의자료 원본 규칙(로컬 서버) `[UPLOAD-BASELINE]` 14줄, "baseline posts in 61.87 s video: 14" | 터미널 경로, 실행 시각 18:03:48, 작업 표시줄 시각 |
| ✅ | `F1_faces.png` | YuNet 얼굴 수 total_raw 59 / total_blur 0, 인원 분포 {0:1196,1:649,2:11} | 터미널 경로, 시각 18:06:48 |
| ✅ | `F1_app_detail.png` | 앱 상세 — 블러된 업로드 이미지 (= stage_3_app_detail) | 상태바 시각 (앱 화면은 계정 표시 없음) |
| ❌ | `F2_admin_posts.png` | admin Posts 목록(인원·등급 열) | **미촬영**: admin 로그인에 비밀번호 입력이 필요하고 AI 는 입력할 수 없음 → 학생이 로그인 후 촬영 |
| ✅ | `F2_app_list.png` | 앱 목록 등급 라벨(보통 노랑/여유 초록) (= f3_green) | 상태바 시각 |
| ✅ | `F3_fresh.png` / `f3_green.png` | 초록 띠 "최종 갱신 시각: 2026-11-25 17:59" (2차 실행 직후) | 상태바 시각 5:59 |
| ✅ | `F3_stale.png` / `f3_red.png` | 빨간 띠 "데이터 오래됨 (최종 갱신 시각: 2026-11-25 17:20)" (= stage_3_app) | 상태바 시각 5:43 |
| ✅ | `F3_nodata.png` | 공학관 스터디룸 → 회색 "아직 데이터가 없습니다." | 상태바 시각 6:07 |
| ✅ | `2-1_tests.png` | `manage.py test -v 2` 8건 OK (test_viewer_read_only 등) | 터미널 경로, 시각 |
| ✅ | `2-2_blog.png` | 0733 이미지 블로그 홈 (1-3 과 같은 화면의 브라우저 부분) | 주소창, 시각 |
| ❌ | `2-2_admin.png` | Django admin | **미촬영**: 위와 같은 이유 (admin 로그인) |
| ✅ | `3-1_list.png` | 앱 목록 (스터디룸 A, = stage_3_app) | 상태바 시각 |
| ✅ | `3-2_detail.png` | 앱 상세 (= stage_3_app_detail) | 상태바 시각 |
| ✅ | `3-3_login.png` | 앱 로그인 화면 (계정 viewer, 온라인 서버, "로그아웃했습니다.") | 계정, 상태바 시각 |
| ✅ | `stage_1_edge_draft.jpg` | 1단계 Edge 터미널 (학생 촬영) | 터미널 |
| ✅ | `stage_2_web.png`, `stage_3_app.png`, `stage_3_app_detail.png`, `stage_all.png` | 단계 연결 증거 (post id 6) | 주소창·시각 / 상태바 시각 / 터미널·주소창·시각 |
| ✅ | `report_materials/demo/demo.mp4` | 시연 영상 69.5초 (2차 실행, post id 13~18) | 터미널 경로, 주소창, 작업 표시줄 시각 |
- 앱 단독 화면은 "상태바 시각" 1개만 보인다 (앱이 계정을 표시하지 않음). 두 항목이 필요하면 `stage_all.png` 처럼 데스크톱 전체(작업 표시줄 시각 + 상태바)로 다시 찍어야 함.
