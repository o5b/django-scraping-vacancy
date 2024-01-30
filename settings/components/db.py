# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
# }


DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': 'scraping',
       'USER': 'scraping',
       'PASSWORD': 'scraping',
       'HOST': '127.0.0.1',
       'PORT': '5432',
   }
}
