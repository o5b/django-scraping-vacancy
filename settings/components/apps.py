DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
]

THIRD_APPS = [
    'debug_toolbar',
    'django_extensions',
    'ckeditor_uploader',
    'ckeditor',
    'django_object_actions',
    'haystack',
    'import_export',
    'django_celery_results',
    'django_celery_beat',
]

CUSTOM_APPS = [
    'applications.core',
    'applications.main',
    'applications.vacancy',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_APPS + CUSTOM_APPS + ['django_cleanup.apps.CleanupConfig',]
