from split_settings.tools import optional, include


include(
    'components/apps.py',
    'components/base.py',
    'components/debug.py',
    'components/logging.py',
    'components/ckeditor.py',
    'components/haystack.py',
    'components/celery.py',
    optional('local_settings.py'),
)
