# 조건 대비표 체크리스트 (진행 중)

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
`python manage.py seed_demo` (blog/management/commands/seed_demo.py)가 만드는 Space 4개(좌석 수 120/80/30/50)는 **데모용 임의 예시 데이터**이며 실제 시설 정보가 아니다.

## 자유 기능 후보 (F1~F3, 학생 확인 필요)
- F1 개인정보 블러: Edge `blur_boxes` (changedetection.py)
- F2 혼잡도 상태: Edge `crowd_level` + Service `Space`/`SpaceViewSet`/`SpaceSerializer.get_latest` + App 목록 라벨
- F3 즐겨찾기 + "여유" 알림: App (미구현)
※ 사람 수 안정 판정(30프레임 + 60초)은 1-3 대체이므로 자유 기능에 넣지 않음.

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
