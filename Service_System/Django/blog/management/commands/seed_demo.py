"""초기화 명령: python manage.py seed_demo

- 관리자(admin), Edge 업로드용 계정(edge) 생성
- 예시 Space 생성 (좌석 수는 데모용 임의 값)
비밀번호는 --admin-password / --edge-password 로 지정하거나,
지정하지 않으면 무작위 생성하여 `seed_credentials.json`(git 제외)에 저장한다.
이미 존재하는 계정/공간은 건드리지 않는다.
"""
import json
import secrets

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from blog.models import Space

SAMPLE_SPACES = [
    # name, building, floor, capacity, has_outlet  (예시 데이터)
    ('중앙도서관 제1열람실', '중앙도서관', '2F', 120, True),
    ('중앙도서관 제2열람실', '중앙도서관', '3F', 80, True),
    ('공학관 스터디룸', '공학관', '1F', 30, False),
    ('학생회관 자습실', '학생회관', 'B1', 50, True),
]


class Command(BaseCommand):
    help = '관리자/Edge 계정과 예시 Space 를 만든다.'

    def add_arguments(self, parser):
        parser.add_argument('--admin-password')
        parser.add_argument('--edge-password')
        parser.add_argument('--reset-passwords', action='store_true',
                            help='이미 있는 계정의 비밀번호도 새로 설정(지정 안 하면 무작위)하고 seed_credentials.json 에 저장')

    def handle(self, *args, **opts):
        creds = {}
        for username, key, is_admin in (('admin', 'admin_password', True),
                                        ('edge', 'edge_password', False)):
            existing = User.objects.filter(username=username).first()
            if existing and opts['reset_passwords']:
                pw = opts[key] or secrets.token_urlsafe(12)
                existing.set_password(pw)
                existing.save()
                creds[username] = pw
                self.stdout.write(f'계정 {username}: 비밀번호 재설정')
                continue
            if existing:
                self.stdout.write(f'계정 {username}: 이미 존재 (건너뜀)')
                continue
            pw = opts[key] or secrets.token_urlsafe(12)
            if is_admin:
                User.objects.create_superuser(username, '', pw)
            else:
                User.objects.create_user(username, password=pw)
            creds[username] = pw
            self.stdout.write(f'계정 {username}: 생성')
        for name, building, floor, cap, outlet in SAMPLE_SPACES:
            _, created = Space.objects.get_or_create(
                name=name, defaults=dict(building=building, floor=floor,
                                         capacity=cap, has_outlet=outlet))
            self.stdout.write(f'공간 {name}: {"생성" if created else "이미 존재"}')
        if creds:
            path = settings.BASE_DIR / 'seed_credentials.json'
            old = json.loads(path.read_text('utf-8')) if path.exists() else {}
            old.update(creds)
            path.write_text(json.dumps(old, indent=2), encoding='utf-8')
            self.stdout.write(f'새 계정 비밀번호를 {path.name} 에 저장했습니다 (git 제외).')
