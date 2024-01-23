from import_export import resources

from . import models


class VacancyResource(resources.ModelResource):

    class Meta:
        model = models.Vacancy
        fields = ('id', 'title', 'body', 'salary', 'address', 'place', 'requirements',
                  'language', 'contact_name', 'contact_phone', 'contact_email', 'vacancy_id', 'text_date', 'datetime',
                  'created', 'company__name', 'scraping_site__link',)


class CompanyResource(resources.ModelResource):

    class Meta:
        model = models.Company
        fields = ('id', 'name', 'about', 'about_short', 'industry', 'employees', 'verified',
                  'website', 'phone', 'email', 'company_id', 'skills', 'company_ratings',
                  'rating', 'statistics', 'addresses', 'contacts', 'links', 'members',
                  'photo', 'video', 'created', 'scraping_site__link',)
