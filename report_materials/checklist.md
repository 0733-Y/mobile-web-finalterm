# 조건 대비표 체크리스트 (진행 중)

| 번호 | 구현(O/X) | 대체(O/X) | 파일 / 함수·클래스 | 설명 |
|---|---|---|---|---|
| 1-1 | O | X | Edge_System/YOLO/detect.py `run()` | YOLOv5s 사전학습 모델 사용 (yolov5s.pt, 첫 실행 시 자동 다운로드) |
| 1-2 | O | O | detect.py `parse_opt()` (`opt.classes=[0]`) | COCO 80클래스 중 person 만 검출 — 대체 |
| 1-3 | O | O | Edge_System/YOLO/changedetection.py `ChangeDetection.update/mark_uploaded`; detect.py `run()` | 물체 유무 대신 사람 수 변화(연속 N프레임 유지)로 변경 감지 — 대체 |
| 1-4 | O | X | changedetection.py `ChangeDetection.get_token`, `ChangeDetection.upload` | token 인증 후 `/api_root/Post/` 로 multipart POST |
| 1-5 | O | X | changedetection.py `blur_boxes`, `crowd_level`; detect.py (`--upload`, `--config`) | 사람 영역 블러(개인정보), 혼잡도 등급 계산, 비디오 파일 입력 지원 |
| 2-1 | O | X | Service_System/Django/config/settings.py (REST_FRAMEWORK: TokenAuthentication), config/urls.py (`obtain_auth_token`) | DRF Token 인증, 헤더 `Authorization: Token <token>`, `/api-token-auth/` |
| 2-2 | O | X | blog/models.py `Post`, `Space`; blog/admin.py `PostAdmin`, `SpaceAdmin`; blog/views.py `post_list`, `post_detail` | 이미지 블로그 + Django admin |
| 2-3 | O | X | blog/views.py `BlogImages` (POST `/api_root/Post/`), `perform_create` | Edge 업로드용 |
| 2-4 | O | X | blog/views.py `BlogImages` (GET 목록/상세), `SpaceViewSet` (`/api_root/Space/`) | 최신순, 페이지네이션, `?space=` 필터 |
| 2-5 | O | X | blog/serializers.py `SpaceSerializer.get_latest`; blog/tests.py `ApiTests` | 공간별 최신 상태, 자동 테스트 5건 통과 (Django 5.2 LTS) |

(1-x, 3-x, PythonAnywhere 배포는 이후 단계에서 추가)

## 예시 데이터 안내
`python manage.py seed_demo` (blog/management/commands/seed_demo.py)가 만드는 Space 4개(좌석 수 120/80/30/50)는 **데모용 임의 예시 데이터**이며 실제 시설 정보가 아니다.
