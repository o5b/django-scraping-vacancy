import os


# Haystack provides modular search for Django
# https://django-haystack.readthedocs.io/en/master/

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}


# Optional: Define the default SearchView for your project

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.BaseSignalProcessor'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
# HAYSTACK_DEFAULT_OPERATOR = 'AND'
# HAYSTACK_DEFAULT_OPERATOR = 'OR'
