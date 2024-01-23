from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.vacancy_list,
        name='vacancy_list',
    ),

    path(
        '<int:pk>/',
        views.vacancy_detail,
        name='vacancy_detail',
    ),

    path(
        'company/',
        views.company_list,
        name='company_list',
    ),

    path(
        'company/<int:pk>/',
        views.company_detail,
        name='company_detail',
    ),

    path(
        'autocomplete/',
        views.autocomplete,
        name='autocomplete',
    ),

    path(
        'search/',
        views.VacancySearchView.as_view(),
        name='haystack_search',
    ),
]
