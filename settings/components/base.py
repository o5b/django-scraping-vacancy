import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '{{ secret_key }}'

DEBUG = False
ALLOWED_HOSTS = []
ADMINS = (('Admin', 'admin.com'),)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'applications.main.processors.preference',
            ],
        },
    },
]

ASGI_APPLICATION = 'settings.asgi.application'
WSGI_APPLICATION = 'settings.wsgi.application'

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'UTC'
# TIME_ZONE = 'Europe/Moscow'
# TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_L10N = True
USE_TZ = True
SITE_ID = 1

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'frontend'),)    # здесь collectstatic также будет искать статические файлы
STATIC_ROOT = os.path.join(BASE_DIR, 'static')              # сюда collectstatic поместит найденные стат. файлы
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
