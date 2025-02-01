"""
Django settings for apiserver project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PDF_SAVE_PATH = os.path.join(BASE_DIR, "report", "reports")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$z%bvmvvn__!qzdmta5j&v#jv#^09o^p)!bzwp1-q_hg@ec26b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '0.0.0.0',
    'django',
    '127.0.0.1',  # 로컬 개발
    'localhost',  # 로컬 개발
    "chrome-extension://flpheaheemmfidkdnokahgmfpehnldkn",  # 확장 프로그램의 origin
    'refactory.store',
    '34.44.174.202'
    'www.refactory.store',
    '55a9-221-151-106-114.ngrok-free.app', # ngrok 도메인 추가
    '6565-221-151-106-114.ngrok-free.app', # ngrok 도메인 추가
    'nginx'
]

CORS_ALLOW_CREDENTIALS = True  # credentials 허용

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',  # GitHub 연동
    'pullrequest',
    'report',
    'repository',
    'user',
    'oauth',
    'partreview',
    'rest_framework',
    'review',
    'drf_yasg',
    'corsheaders',
    'storages',
    'django_prometheus',
]

CORS_ALLOWED_ORIGINS = [
    "chrome-extension://flpheaheemmfidkdnokahgmfpehnldkn",  # 확장 프로그램의 origin
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
    "http://localhost",
    "http://localhost:5173",
    "http://django:8000",
    "https://github.com",
    "http://www.refactory.store",
    "http://refactory.store",
    "https://www.refactory.store",
    "https://refactory.store",
]

CORS_ALLOW_HEADERS = [
    'authorization',
    'x-password',
    'content-type',
    'x-csrftoken',
    'accept',
    'origin',
    'user-agent',
    'access-control-allow-origin',
    'x-requested-with',
    'accept-encoding',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # 기본 인증
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth 인증
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # 이 줄을 추가
]

ROOT_URLCONF = 'apiserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'apiserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases



# .env 파일 로드
load_dotenv()
# PyMySQL을 사용하도록 설정
import pymysql
pymysql.install_as_MySQLdb()
# DATABASES 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE'),  # .env에서 데이터베이스 이름 가져오기
        #  도커로 실행할 때
        'USER': os.getenv('MYSQL_USER'),      # .env에서 사용자 이름 가져오기
        'PASSWORD': os.getenv('MYSQL_PASSWORD'),  # .env에서 비밀번호 가져오기
        'HOST': 'mysqldb',

        # 로컬에서 실행할 때
        # 'USER': os.getenv("MYSQL_ROOT_USER"),      # .env에서 사용자 이름 가져오기
        # 'PASSWORD': os.getenv('MYSQL_ROOT_PASSWORD'),  # .env에서 비밀번호 가져오기
        # 'HOST': 'localhost',


        'PORT': '3306',  # MySQL 기본 포트
        'OPTIONS': {
            'charset': 'utf8mb4',  # 문자 인코딩 설정
        },
    }
}

# AWS S3 설정
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'

AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',  # JSON 응답만 반환
    ],
}

DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", 'https://api.deepseek.com')
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Celery 메세지 브로커 설정
# Celery 설정
CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672//'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'
CELERY_ENABLE_UTC = False

CSRF_TRUSTED_ORIGINS = [
    "chrome-extension://flpheaheemmfidkdnokahgmfpehnldkn",  # 확장 프로그램의 origin
    'http://localhost:5173',
    'http://localhost',
    'http://localhost:8000',
    "http://www.refactory.store",
    "http://refactory.store",
    "https://www.refactory.store",
    "https://refactory.store"
]
