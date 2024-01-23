from django.db import models
from django.urls import reverse, reverse_lazy

from applications.core import models as core_models


class VacancySite(core_models.Date):
    """
    Сайт откуда взяты вакансии
    """

    class Country(models.TextChoices):
        RUSSIA = 'RUS', 'Россия'
        UKRAINE = 'UKR', 'Украина'
        BELARUS = 'BLR', 'Белоруссия'
        KAZAKHSTAN = 'KAZ', 'Казахстан'
        UZBEKISTAN = 'UZB', 'Узбекистан'
        AMERICA = 'USA', 'США'
        EUROPE = 'EU', 'Европейский Союз'
        ENGLAND = 'GBR', 'Великобритания'
        GERMANY = 'DEU', 'Германия'
        POLAND = 'POL', 'Польша'

    name = models.CharField(
        verbose_name='Название сайта',
        max_length=250,
        blank=True,
    )

    link = models.URLField(
        verbose_name='Ссылка на сайт',
        max_length=1000,
    )

    country = models.CharField(
        verbose_name='Страна',
        max_length=3,
        choices=Country.choices,
        default=Country.RUSSIA,
        blank=True,
    )

    description = models.TextField(
        verbose_name='Описание',
        blank=True,
    )

    class Meta:
        verbose_name = 'сайт вакансий'
        verbose_name_plural = 'сайты вакансий'

    def __str__(self):
        return self.link


class ScrapingLink(core_models.Date):
    """
    Ссылка для скрапинга вакансий
    """

    skill = models.CharField(
        verbose_name='Навык',
        max_length=100,
    )

    link = models.URLField(
        verbose_name='Ссылка для скрапинга',
        max_length=1000,
        help_text='Пример: https://career.habr.com/vacancies?q=python&sort=date&type=all',
    )

    scraping_site = models.ForeignKey(
        verbose_name='Скрапинг на сайте',
        to=VacancySite,
        on_delete=models.CASCADE,
    )

    description = models.TextField(
        verbose_name='Описание',
        blank=True,
    )

    class Meta:
        verbose_name = 'ссылку для скрапинга'
        verbose_name_plural = 'ссылки для скрапинга'

    def __str__(self):
        return self.link


class Company(core_models.Common):
    """
    Компания разместившая вакансию
    """

    name = models.CharField(verbose_name='Название компании', max_length=250)
    slug = models.SlugField(verbose_name='URL-имя', max_length=250, blank=True)
    about = models.TextField(verbose_name='О компании', blank=True)
    industry = models.CharField(verbose_name='Отрасль', max_length=250, blank=True)
    employees = models.CharField(verbose_name='Количество сотрудников', max_length=250, blank=True)
    verified = models.CharField(verbose_name='Компания проверена', max_length=250, blank=True)
    website = models.CharField(verbose_name='Сайт компании', max_length=250, blank=True)
    phone = models.CharField(verbose_name='Телефон компании', max_length=250, blank=True)
    email = models.CharField(verbose_name='E-mail компании', max_length=250, blank=True)
    company_id = models.CharField(verbose_name='ID компании', max_length=250, blank=True)
    scraping_site = models.ForeignKey(verbose_name='Компания с сайта', to=VacancySite, on_delete=models.SET_NULL, null=True, blank=True)
    about_short = models.TextField(verbose_name='О компании (сокращённо)', blank=True)
    skills = models.CharField(verbose_name='Навыки', max_length=1000, blank=True)
    company_ratings = models.CharField(verbose_name='Рейтинги и оценки', max_length=250, blank=True)
    rating = models.CharField(verbose_name='Средний рейтинг компании', max_length=100, blank=True)
    statistics = models.CharField(verbose_name='Статистика', max_length=1000, blank=True)
    addresses = models.TextField(verbose_name='Адреса компании', blank=True)
    contacts = models.TextField(verbose_name='Контакты', blank=True)
    links = models.TextField(verbose_name='Ссылки', blank=True)
    members  =  models.JSONField(verbose_name='Персонал компании', blank=True, null=True)
    photo = models.JSONField(verbose_name='Фото компании', blank=True, null=True)
    video = models.JSONField(verbose_name='Видео компании', blank=True, null=True)

    class Meta:
        verbose_name = 'компанию'
        verbose_name_plural = 'компании'

    def get_absolute_url(self):
        return reverse('vacancy:company_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class Vacancy(core_models.Common):
    """
    Вакансия
    """

    title = models.CharField(verbose_name='Название вакансии', max_length=250)
    slug = models.SlugField(verbose_name='URL-имя', max_length=250, blank=True)
    body = models.TextField(verbose_name='Текст вакансии')
    salary = models.CharField(verbose_name='Зарплата', max_length=250, blank=True)
    address = models.CharField(verbose_name='Адрес работы', max_length=250, blank=True)
    place = models.CharField(verbose_name='Место работы', max_length=250, blank=True)
    requirements = models.CharField(verbose_name='Условия и требования', max_length=250, blank=True)
    language = models.CharField(verbose_name='Знание языков', max_length=250, blank=True)
    contact_name = models.CharField(verbose_name='Контактное имя', max_length=250, blank=True)
    contact_phone = models.CharField(verbose_name='Контактный телефон', max_length=50, blank=True)
    contact_email = models.CharField(verbose_name='Контактный e-mail', max_length=100, blank=True)
    company = models.ForeignKey(verbose_name='Компания', to=Company, on_delete=models.CASCADE, null=True, blank=True)
    vacancy_id = models.CharField(verbose_name='ID вакансии', max_length=250)
    scraping_site = models.ForeignKey(verbose_name='Вакансия с сайта', to=VacancySite, on_delete=models.SET_NULL, null=True, blank=True)
    scraping_link = models.ForeignKey(verbose_name='Ссылка для скрапинга', to=ScrapingLink, on_delete=models.SET_NULL, null=True, blank=True)
    text_date = models.CharField(verbose_name='День создания (текст с сайта вакансий)', max_length=250, blank=True)
    datetime = models.DateTimeField(verbose_name='Дата и время создания на сайте вакансий', blank=True, null=True)

    class Meta:
        ordering = ['-datetime']
        verbose_name = 'вакансию'
        verbose_name_plural = 'вакансии'

    def get_absolute_url(self):
        return reverse_lazy('vacancy:vacancy_detail', kwargs={'pk': self.pk})
    get_absolute_url.short_description = 'ссылка'

    def __str__(self):
        return self.title
