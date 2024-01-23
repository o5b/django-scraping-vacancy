from django.contrib import admin, messages
from django_object_actions import DjangoObjectActions
from import_export.admin import ExportActionModelAdmin

from applications.core.admin import CommonAdmin
from applications.vacancy import resources
from applications.vacancy.models import (Company, ScrapingLink, Vacancy, VacancySite)
from applications.vacancy.parser.career_habr_com import ParserCareerHabrCom
from applications.vacancy.parser.work_ua import ParserWorkUa


@admin.register(Vacancy)
class VacancyAdmin(ExportActionModelAdmin, CommonAdmin):
    list_display = ['title', 'id', 'scraping_site', 'get_skill', 'text_date', 'datetime', 'created', 'company']
    list_filter = ['status', 'scraping_site', 'created', 'scraping_link__skill']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['vacancy_id', 'scraping_site', 'scraping_link', 'company', 'text_date', 'datetime', 'created', 'modified']
    ordering = ['-datetime']
    resource_class = resources.VacancyResource

    def get_skill(self, obj):
        if obj.scraping_link:
            return obj.scraping_link.skill
        else:
            return None

    get_skill.short_description = 'Навык'


@admin.register(Company)
class CompanyAdmin(ExportActionModelAdmin, CommonAdmin):
    list_display = ['name', 'id', 'scraping_site', 'slug']
    list_filter = ['created', 'scraping_site']
    search_fields = ['name', 'about']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['company_id', 'scraping_site', 'created', 'modified']
    resource_class = resources.CompanyResource


@admin.register(VacancySite)
class VacancySiteAdmin(admin.ModelAdmin):
    list_display = ['link', 'name', 'id', 'country']
    list_filter = ['created', 'country']
    search_fields = ['name']
    readonly_fields = ['created', 'modified']


@admin.register(ScrapingLink)
class ScrapingLinkAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ['skill', 'id', 'scraping_site']
    list_filter = ['created', 'scraping_site']
    search_fields = ['skill']
    readonly_fields = ['created', 'modified']
    change_actions = ['vacancy_scraping']

    def vacancy_scraping(self,  request, obj):
        if 'https://www.work.ua' in obj.scraping_site.link:
            bot = ParserWorkUa(obj.id, None)
        elif 'https://career.habr.com' in obj.scraping_site.link:
            bot = ParserCareerHabrCom(obj.id, None)
        try:
            bot.scraping()
            messages.add_message(request, messages.SUCCESS, 'SUCCESS: Вакансии получены!')
        except Exception as er:
            print('Scraping: {0} -> finished Error: {1}'.format(obj.scraping_site.link, er))
            messages.add_message(request, messages.ERROR, f'ERROR: {er}.')

    vacancy_scraping.label = 'Начать Скрапинг'
    vacancy_scraping.short_description = 'Скрапинг может занять много времени, в зависимости от количества вакансий'
