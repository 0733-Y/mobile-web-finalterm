"""Edge 측 변경 감지 + 업로드 (1-3, 1-4, 1-5).

ChangeDetection
  - 사람 수가 현재 상태와 달라지고 `stable_frames` 프레임 연속 유지되면 "변화"로 판정
  - 마지막 업로드로부터 `min_interval_sec` 초가 지나야 업로드
  - 업로드 전 사람 영역 블러 (개인정보 보호, 1-5 추가기능)
  - 서버 인증: /api-token-auth/ 로 token 을 받아 `Authorization: Token <token>`
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import requests


def load_config(path='config.json'):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def crowd_level(count, capacity):
    """<40% 여유, 40~80% 보통, >=80% 혼잡."""
    ratio = count / capacity if capacity else 0
    if ratio < 0.4:
        return '여유'
    if ratio < 0.8:
        return '보통'
    return '혼잡'


def blur_boxes(frame, boxes, ksize=51):
    """boxes: [(x1, y1, x2, y2), ...] 영역을 가우시안 블러."""
    h, w = frame.shape[:2]
    for x1, y1, x2, y2 in boxes:
        x1, y1, x2, y2 = max(0, int(x1)), max(0, int(y1)), min(w, int(x2)), min(h, int(y2))
        if x2 > x1 and y2 > y1:
            frame[y1:y2, x1:x2] = cv2.GaussianBlur(frame[y1:y2, x1:x2], (ksize, ksize), 0)
    return frame


class ChangeDetection:
    def __init__(self, cfg):
        self.server = cfg['server'].rstrip('/')
        self.username = cfg['username']
        self.password = cfg['password']
        self.space_id = cfg['space_id']
        self.capacity = cfg['capacity']
        self.stable_frames = cfg.get('stable_frames', 30)
        self.min_interval = cfg.get('min_interval_sec', 60)
        self.token = None
        self.state = None            # 서버에 마지막으로 보고한(현재 상태) 인원 수
        self._candidate = None
        self._streak = 0
        self._last_upload = float("-inf")

    # ---- 인증 ----
    def get_token(self):
        r = requests.post(f'{self.server}/api-token-auth/',
                          data={'username': self.username, 'password': self.password},
                          timeout=15)
        r.raise_for_status()
        self.token = r.json()['token']
        return self.token

    # ---- 업로드 (1-4) ----
    def upload(self, frame, count, title=None, text=''):
        if self.token is None:
            self.get_token()
        ok, buf = cv2.imencode('.jpg', frame)
        if not ok:
            raise ValueError('이미지 인코딩 실패')
        now = datetime.now(timezone.utc).isoformat()
        data = {
            'title': title or f'space{self.space_id} {count}명',
            'text': text,
            'published_date': now,
            'space': self.space_id,
            'person_count': count,
            'level': crowd_level(count, self.capacity),
        }
        r = requests.post(f'{self.server}/api_root/Post/', data=data,
                          files={'image': ('snapshot.jpg', buf.tobytes(), 'image/jpeg')},
                          headers={'Authorization': f'Token {self.token}'}, timeout=30)
        r.raise_for_status()
        return r.json()

    # ---- 변화 판정 (1-3) ----
    def update(self, count, now=None):
        """프레임마다 호출. 업로드해야 하면 True."""
        now = time.time() if now is None else now
        if count == self.state:
            self._candidate, self._streak = None, 0
            return False
        if count == self._candidate:
            self._streak += 1
        else:
            self._candidate, self._streak = count, 1
        if self._streak < self.stable_frames:
            return False
        if now - self._last_upload < self.min_interval:
            return False
        return True

    def mark_uploaded(self, count, now=None):
        self.state = count
        self._candidate, self._streak = None, 0
        self._last_upload = time.time() if now is None else now
