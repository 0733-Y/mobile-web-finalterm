"""Edge 측 변경 감지 + 업로드 (1-3, 1-4, 1-5).

ChangeDetection
  - 사람 수가 현재 상태와 달라지고 `stable_frames` 프레임 연속 유지되면 "변화"로 판정
  - 마지막 업로드로부터 `min_interval_sec` 초가 지나야 업로드
  - 업로드 전 사람 영역 블러 (개인정보 보호, 1-5 추가기능)
  - 서버 인증: /api-token-auth/ 로 token 을 받아 `Authorization: Token <token>`
"""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import requests


# 환경변수가 있으면 config.json 값을 덮어쓴다 (비밀번호를 파일에 두지 않기 위함)
ENV_OVERRIDES = {
    'SPACECHECK_SERVER': 'server',
    'SPACECHECK_USERNAME': 'username',
    'SPACECHECK_PASSWORD': 'password',
}


def load_config(path='config.json'):
    cfg = json.loads(Path(path).read_text(encoding='utf-8'))
    for env, key in ENV_OVERRIDES.items():
        if os.environ.get(env):
            cfg[key] = os.environ[env]
    return cfg


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
        self.min_interval = cfg.get('min_interval_sec', 10)  # 학생 동의로 60초 -> 10초 (2026-11-24)
        # 업로드 제목 = "<title_prefix> | <space_name> | N명" (보고서 증거용 학번 뒤 4자리를 prefix 로 설정)
        self.title_prefix = cfg.get('title_prefix', '')
        self.space_name = cfg.get('space_name', f"space{cfg['space_id']}")
        # mode: 'count'(기본, 사람 수 변화+안정 프레임+최소 간격) / 'baseline'(강의자료 원본: 없음→있음이면 업로드)
        self.mode = cfg.get('mode', 'count')
        self._result_prev = {}       # baseline: 클래스 이름 -> 직전 프레임 존재 여부(0/1)
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

    def make_title(self, count):
        parts = [self.title_prefix, self.space_name, f'{count}명']
        return ' | '.join(p for p in parts if p)

    # ---- 업로드 (1-4) ----
    def upload(self, frame, count, title=None, text=''):
        if self.token is None:
            self.get_token()
        ok, buf = cv2.imencode('.jpg', frame)
        if not ok:
            raise ValueError('이미지 인코딩 실패')
        now = datetime.now(timezone.utc).isoformat()
        data = {
            'title': title or self.make_title(count),
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

    # ---- 강의자료(ch08) 원본 규칙 (비교 측정용, --mode baseline) ----
    def update_baseline(self, present_names):
        """present_names: 현재 프레임에서 검출된 클래스 이름들(80개 COCO 전체 대상).
        클래스마다 result_prev 를 두고, 어느 한 클래스라도 0 -> 1 이 되면 즉시 업로드 대상.
        안정 프레임·최소 간격·사람 수 개념 없음. 새로 나타난 클래스 이름 리스트를 반환."""
        new = [n for n in present_names if not self._result_prev.get(n)]
        self._result_prev = {n: 1 for n in present_names}
        return new

    def upload_baseline(self, frame, new_names):
        """ch08 원본 업로드: 새로 0->1 이 된 클래스마다 title 을 덮어써서 마지막 클래스 이름이 제목이 되고,
        본문은 각 클래스 이름 뒤에 ", " 를 붙여 이어 쓴다(끝의 쉼표 유지). 이미지 320x240.
        (space/person_count/level/블러 없음 — 강의자료 필드만 전송. 제목 앞에는 증거용 접두어만 붙인다)"""
        if self.token is None:
            self.get_token()
        small = cv2.resize(frame, (320, 240))
        ok, buf = cv2.imencode('.jpg', small)
        if not ok:
            raise ValueError('이미지 인코딩 실패')
        title, text = '', ''
        for name in new_names:
            title = name
            text += name + ', '
        title = ' | '.join(p for p in (self.title_prefix, title) if p)
        data = {'title': title, 'text': text,
                'published_date': datetime.now(timezone.utc).isoformat()}
        r = requests.post(f'{self.server}/api_root/Post/', data=data,
                          files={'image': ('snapshot.jpg', buf.tobytes(), 'image/jpeg')},
                          headers={'Authorization': f'Token {self.token}'}, timeout=30)
        r.raise_for_status()
        return r.json()

    def mark_uploaded(self, count, now=None):
        self.state = count
        self._candidate, self._streak = None, 0
        self._last_upload = time.time() if now is None else now
