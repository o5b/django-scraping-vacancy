from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path


urlpatterns = [
    path(
        'admin/',
        admin.site.urls,
    ),
]

urlpatterns += [
    path(
        'ckeditor/',
        include('ckeditor_uploader.urls'),
    ),
]

urlpatterns += [
    path(
        '',
        include(('applications.main.urls', 'main'), namespace='main'),
    ),

    path(
        'vacancy/',
        include(('applications.vacancy.urls', 'vacancy'), namespace='vacancy'),
    ),
]

urlpatterns += staticfiles_urlpatterns() + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
