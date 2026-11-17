# 데모 시나리오 (작성 중 — Edge 부분)

## Edge: 비디오 입력 → 검출 → 변화 시 업로드
전제: Django 서버가 8000 포트에서 실행 중, `Edge_System/YOLO/config.json` 에 edge 계정 정보가 있음, `demo.mp4` 준비됨 (README 참고).
```bash
cd Service_System/Django && python manage.py runserver
cd Edge_System/YOLO && venv/Scripts/python detect.py --source demo.mp4 --config config.json --upload --stable-frames 20 --min-interval 2
```
기대 결과: 로그에 `[UPLOAD] persons=0/1/3/4` 4줄, 서버 `http://127.0.0.1:8000/` 및 `/admin/` 에서 새 Post 4개, 이미지의 사람은 블러 처리됨.
혼잡도 등급을 다양하게 보이려면 config.json 의 `capacity` 를 6 으로 낮춘다 (0명·1명=여유, 3·4명=보통).
