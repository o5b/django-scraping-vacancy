from django.conf import settings


# django-querycount
# django-debug-toolbar
settings.MIDDLEWARE += [
    'querycount.middleware.QueryCountMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# django-debug-toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]
