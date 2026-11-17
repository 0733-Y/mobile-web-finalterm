"""
SpaceCheck Django settings.

비밀값(SECRET_KEY 등)은 환경변수 또는 저장소에 올리지 않는 `local_settings.json`에서 읽는다.
예시: `local_settings.example.json` 참고.
"""

import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- 로컬 비공개 설정 (git 제외) -------------------------------------------
_local = {}
_local_path = BASE_DIR / 'local_settings.json'
if _local_path.exists():
    _local = json.loads(_local_path.read_text(encoding='utf-8'))


def _get(name, default=None):
    return os.environ.get(name, _local.get(name, default))


SECRET_KEY = _get('SECRET_KEY', 'dev-only-insecure-key-change-me')
DEBUG = str(_get('DEBUG', 'true')).lower() == 'true'

# PythonAnywhere: "<username>.pythonanywhere.com" 을 local_settings.json 의 ALLOWED_HOSTS 에 추가
_hosts = _get('ALLOWED_HOSTS', 'localhost,127.0.0.1,10.0.2.2')
ALLOWED_HOSTS = _hosts if isinstance(_hosts, list) else [h.strip() for h in _hosts.split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'   # PythonAnywhere: collectstatic 대상
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'     # 업로드 이미지 (git 제외)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- DRF: Token 인증 (요청 헤더 `Authorization: Token <token>`) -------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
