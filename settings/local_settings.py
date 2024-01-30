import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = 'django-insecure-pkp&df0v!a&4+@gb*&%9bj5bej4(o&nea*llhj)s03cw8x!ow^'


# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
# }


# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': 'scraping',
#        'USER': 'scraping',
#        'PASSWORD': 'scraping',
#        'HOST': '127.0.0.1',
#        'PORT': '5432',
#    }
# }


#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'tmp/app-messages')
