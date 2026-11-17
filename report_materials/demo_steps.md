# 데모 시나리오 (작성 중 — Edge 부분)

입력은 **본인 웹캠 또는 본인이 촬영한 영상**만 사용한다 (인터넷 영상 금지, 템플릿 v2.0).

## Edge: 입력 → 검출 → 변화 시 업로드
전제: 서버 실행 중, `Edge_System/YOLO/config.json`(server, username, password, `title_prefix`=5960 ...) 준비.
비밀번호는 환경변수 `SPACECHECK_PASSWORD` 로 줄 수도 있음.
```bash
# 웹캠
venv/Scripts/python detect.py --source 0 --config config.json --upload
# 본인 영상 (파일은 Edge_System/YOLO/ 에 두고 저장소에는 올리지 않음)
venv/Scripts/python detect.py --source my_video.mp4 --config config.json --upload
# 강의자료 원본 규칙 측정 (필요성 페이지용)
venv/Scripts/python detect.py --source 0 --config config.json --upload --mode baseline
```
기대 결과: 로그에 `[UPLOAD] persons=N -> post id=...`, 서버 Post 제목이 `5960 | 중앙도서관 제1열람실 | N명`.
