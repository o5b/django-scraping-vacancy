import datetime
import random
import time

import pytils
import requests
from bs4 import BeautifulSoup
from django.utils.text import slugify

from applications.vacancy.models import (Company, ScrapingLink, Vacancy, VacancySite)


class ParserWorkUa:
    """ Для получения вакансий и компаний с сайта work.ua """

    def __init__(self, link_id, skill):
        self.link_id = link_id
        self.skill = skill

    def get_user_agent(self) -> dict:
        user_agent =  {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}
        return user_agent

    def scraping(self, *args, **options):
        vacancies_list = []
        companies_list = []
        scraping_stop = False
        latest_vacancy = ''
        url = ''
        scraping_site_obj = VacancySite.objects.get(link='https://www.work.ua')
        if self.link_id:
            try:
                scraping_link_obj = ScrapingLink.objects.get(id=self.link_id)
            except Exception as er:
                print('Error get Scraping Link: ', er)

            if scraping_link_obj:
                latest_vacancies = Vacancy.objects.filter(scraping_link=scraping_link_obj)

        elif self.skill:
            scraping_link_obj = ScrapingLink.objects.filter(scraping_site=scraping_site_obj, skill=self.skill).first()
            latest_vacancies = Vacancy.objects.filter(scraping_site=scraping_site_obj, scraping_link__skill=self.skill)

        if latest_vacancies:
            latest_vacancy = latest_vacancies.latest('datetime')
            print('latest_vacancy: {}, {}, {}'.format(
                latest_vacancy.vacancy_id, latest_vacancy.title, latest_vacancy.datetime))

        if scraping_link_obj:
            try:
                url = scraping_link_obj.link
            except Exception as er:
                print('Error get url: ', er)

        if not url:
            scraping_stop = True

        while not scraping_stop:
            print('url: ', url)
            time.sleep(10)
            response = requests.get(url, headers=self.get_user_agent())
            url = None

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                if soup:
                    vacancies_from_current_page = soup.select("div.card.card-hover.card-search.card-visited.wordwrap.job-link")

                    if vacancies_from_current_page:
                        print('############## page ############# vacancy count: ', len(vacancies_from_current_page))

                        for data in vacancies_from_current_page:
                            vacancy_link = ''
                            vacancy_link = data.find('a')
                            print('vacancy_link: ', vacancy_link['href'] if 'href' in vacancy_link else vacancy_link)

                            if vacancy_link:
                                vacancy_id = vacancy_link['href'].split('/')[-2]

                                if vacancy_id.isdigit() and (vacancy_id not in vacancies_list):
                                    vacancies_list.append(vacancy_id)
                                    print('vacancies_list: ', len(vacancies_list))
                                    time.sleep(random.randint(2, 3))
                                    vacancy_data = self.vacancy(vacancy_id)

                                    if vacancy_data:
                                        datetime_now = datetime.datetime.now()

                                        if not vacancy_data['text_date']:
                                            vacancy_data['text_date'] = pytils.dt.ru_strftime(
                                                'Вакансия от %d %B %Y',
                                                inflected=True,
                                                date=datetime_now,
                                            )

                                        date_values = self.get_vacancy_date(vacancy_data['text_date'])

                                        # str_datetime = '{}-{}-{}T{}:{}:{}{}'.format(
                                        #     date_values['year'],
                                        #     date_values['month'],
                                        #     date_values['day'],
                                        #     datetime_now.hour,
                                        #     datetime_now.minute,
                                        #     datetime_now.second,
                                        #     # '+0300',    # Мск
                                        #     '+0200',    # Киев
                                        # )

                                        # на work.ua указывают только дату, время с timezone (+0200 Киев) добавляем сами
                                        str_datetime = '{}-{}-{}T02:00:01+0200'.format(
                                            date_values['year'], date_values['month'], date_values['day'])

                                        vacancy_datetime = datetime.datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%S%z')

                                        print("vacancy_data['text_date']: {} ==> vacancy_datetime: {}".format(
                                            vacancy_data['text_date'], vacancy_datetime))

                                        if latest_vacancy:
                                            print('latest_vacancy.datetime: {} >= vacancy_datetime: {} >>>> {}'.format(
                                                latest_vacancy.datetime,
                                                vacancy_datetime,
                                                latest_vacancy.datetime >= vacancy_datetime
                                                )
                                            )

                                            if latest_vacancy.datetime >= vacancy_datetime:
                                                scraping_stop = True
                                                break

                                        company_id = vacancy_data['company_id']
                                        print('company_id: ', company_id)

                                        if company_id not in companies_list:
                                            companies_list.append(company_id)
                                            print('companies_list: ', len(companies_list))

                                            time.sleep(random.randint(2, 3))
                                            company_data = self.company(company_id)

                                            if company_data:
                                                company, created = Company.objects.update_or_create(
                                                    company_id=company_id,
                                                    defaults={
                                                        'name': company_data['name'],
                                                        'slug': slugify(pytils.translit.slugify(company_data['name'][:50])),
                                                        'about': company_data['about'],
                                                        'verified': company_data['verified'],
                                                        'employees': company_data['employees'],
                                                        'industry': company_data['industry'],
                                                        'website': company_data['website'],
                                                        'phone': company_data['phone'],
                                                        'email': company_data['email'],
                                                        'company_id': company_id,
                                                        'photo': company_data['company_photo'],
                                                        'video': company_data['company_video'],
                                                        'scraping_site': scraping_site_obj,
                                                    },
                                                )

                                        elif (company_id in companies_list) or not company_data:
                                            company = Company.objects.filter(company_id=company_id).first()

                                        vacancy_slug = '{0}-{1}-{2}'.format(
                                            vacancy_id,
                                            company.slug if company else '',
                                            slugify(pytils.translit.slugify(vacancy_data['title'][:50]))
                                        )

                                        vacancy, vacancy_created = Vacancy.objects.update_or_create(
                                            vacancy_id=vacancy_id,
                                            defaults={
                                                'title': vacancy_data['title'],
                                                'body': vacancy_data['description'],
                                                'slug': vacancy_slug,
                                                'text_date': vacancy_data['text_date'],
                                                'datetime': vacancy_datetime if vacancy_datetime else datetime_now,
                                                'salary': vacancy_data['salary'],
                                                'address': vacancy_data['work_address'],
                                                'place': vacancy_data['place_of_work'],
                                                'requirements': vacancy_data['conditions_and_requirements'],
                                                'language': vacancy_data['language_proficiencies'],
                                                'contact_name': vacancy_data['contact_name'],
                                                'contact_phone': vacancy_data['contact_phone'],
                                                'company': company if company else '',
                                                'vacancy_id': vacancy_id,
                                                'scraping_site': scraping_site_obj,
                                                'scraping_link': scraping_link_obj,
                                            }
                                        )

                                print('--------------------------')

                    pagination = soup.find("ul", class_="pagination hidden-xs")
                    if pagination:
                        next_page = pagination.find("span", class_="glyphicon glyphicon-top glyphicon-fs-24 glyphicon-chevron-right")
                        if next_page and ("href" in next_page.parent.attrs):
                            url = f'https://www.work.ua{next_page.parent["href"]}'
                        else:
                            scraping_stop = True
                    else:
                        scraping_stop = True

            else:
                scraping_stop = True
                print('Error: {}, url: {}'.format(response.status_code, url))


    def vacancy(self, vacancy_id: str) -> dict:
        vacancy_data = {
            'text_date': '',
            'datetime': '',
            'title': '',
            'salary': '',
            'work_address': '',
            'place_of_work': '',
            'conditions_and_requirements': '',
            'language_proficiencies': '',
            'contact_name': '',
            'contact_phone': '',
            'company_id': '',
            'description': '',
        }

        url = f'https://www.work.ua/ru/jobs/{vacancy_id}/'
        response = requests.get(url, headers=self.get_user_agent())

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            if soup:
                vacancy_card_select = soup.select("div.card.wordwrap")
                vacancy_card = vacancy_card_select[0]

                if vacancy_card:
                    date = vacancy_card.find('span', class_='text-default-7 add-right-xs add-bottom-sm')

                    if date:
                        # vacancy_data['date'] = date.string
                        vacancy_data['text_date'] = date.get_text().replace('\xa0', ' ').strip()

                    title = vacancy_card.find(id='h1-name')
                    if title:
                        vacancy_data['title'] = title.get_text().strip()

                    description = vacancy_card.find(id='job-description')
                    if description:
                        vacancy_data['description'] = description.get_text().strip()

                    other_info = vacancy_card.find_all('p', class_='text-indent add-top-sm')
                    if other_info:
                        for data in other_info:
                            info = data.find('span')
                            if info:
                                if info['title'] in ['Work address', 'Адрес работы', 'Адреса роботи']:
                                    vacancy_data['work_address'] = data.get_text().strip()
                                elif info['title'] in ['Place of work', 'Место работы', 'Місце роботи']:
                                    vacancy_data['place_of_work'] = data.get_text().strip()
                                elif info['title'] in ['Conditions and requirements', 'Условия и требования', 'Умови й вимоги']:
                                    vacancy_data['conditions_and_requirements'] = data.get_text().strip()
                                elif info['title'] in ['Language proficiencies', 'Знание языков', 'Знання мов']:
                                    vacancy_data['language_proficiencies'] = data.get_text().strip()
                                elif info['title'] in ['Salary', 'Зарплата', 'Зарплата']:
                                    vacancy_data['salary'] = data.get_text().strip()
                                # elif info['title'] in ['Contact us', 'Контакты', 'Контакти']:
                                #     vacancy_data['contact_name'] = data.get_text().strip()
                                elif info['title'] in ['Company Information', 'Данные о компании', 'Дані про компанію']:
                                    company_link = data.find('a')
                                    company_id = company_link['href'].split('/')[-2]
                                    vacancy_data['company_id'] = company_id
                                else:
                                    print("************ def vacancy >> info['title']: ***********", info)

                    contact_phone = vacancy_card.find(id='contact-phone')
                    if contact_phone:
                        contact_name = contact_phone.parent.find('span', class_='add-right-sm')
                        if contact_name:
                            vacancy_data['contact_name'] = contact_name.get_text().strip()
                        phone = contact_phone.find('a', class_='visible-xs-inline js-get-phone hovered')
                        if phone:
                            vacancy_data['contact_phone'] = phone.get_text().strip()

        else:
            print('Error: {}, url: {}'.format(response.status_code, url))
            return {}

        # for k, v in vacancy_data.items():
        #     print('{}: {}'.format(k, v))
        # print("************")

        return vacancy_data


    def company(self, company_id: str) -> dict:
        company_data = {
            'name': '',
            'verified': '',
            'industry': '',
            'employees': '',
            'website': '',
            'phone': '',
            'email': '',
            'about': '',
            'ukrainized': '',
            'company_photo': [],
            'company_video': [],
        }

        url = f'https://www.work.ua/ru/jobs/by-company/{company_id}/'
        response = requests.get(url, headers=self.get_user_agent())

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            if soup:
                company_card_select = soup.select("div.card.wordwrap")
                company_card = company_card_select[0]

                if company_card:

                    company_name = company_card.find('h1', class_='add-bottom-sm text-center')
                    if company_name:
                        company_data['name'] = company_name.get_text().strip()

                    company_industry = company_card.find(
                        'span', class_='glyphicon glyphicon-company text-default glyphicon-large')
                    if company_industry:
                        company_data['industry'] = company_industry.parent.get_text().strip()

                    company_employees = company_card.find(
                        'span', class_='glyphicon glyphicon-employees text-default glyphicon-large')
                    if company_employees:
                        company_data['employees'] = company_employees.parent.get_text().strip()

                    company_website = company_card.find('span', class_='website-company block')
                    if company_website:
                        company_website = company_website.find('a')
                        company_data['website'] = company_website['href']

                    company_verified = company_card.find('span', class_='label label-green-100 add-right-xs add-left-xs add-top-sm')
                    if company_verified:
                        company_data['verified'] = company_verified.get_text().strip()

                    company_ukrainized = company_card.find('span', class_='label label-blue-mariner-100 add-right-xs add-left-xs add-top-sm')
                    if company_ukrainized:
                        company_data['ukrainized'] = company_ukrainized.get_text().strip()

                    company_phone = company_card.find(
                        'span', class_='glyphicon glyphicon-phone text-default glyphicon-large')
                    if company_phone:
                        email = ''
                        print('company_phone: ', company_phone)
                        company_phone_text = company_phone.parent.get_text().replace('\xa0', ' ').strip()
                        if '[email protected]' in company_phone_text:
                            if 'data-cfemail' in company_phone.parent.a.attrs:
                                protected_email = company_phone.parent.a['data-cfemail']
                                if protected_email:
                                    email = self.email_decode(protected_email)
                        if email:
                            company_data['phone'] = company_phone_text.replace('[email protected]', email)
                            company_data['email'] = email
                        else:
                            company_data['phone'] = company_phone_text

                about_company = soup.find(id='about-company')
                if about_company:
                    # удаляем элемент 'Читать еще' при клике на который отображается весь текст
                    remove_element = about_company.find('a', class_='short-description-toggle')
                    if remove_element:
                        remove_element.decompose()
                    company_data['about'] = about_company.get_text().strip()

                company_photo_id = soup.find(id='company-photo')
                if company_photo_id:
                    light_slider_id = company_photo_id.find(id='lightSlider')
                    if light_slider_id:
                        media_list = light_slider_id.find_all('li')
                        for media in media_list:
                            if 'class' in media.attrs:
                                if 'video-slide' in media['class']:
                                    company_data['company_video'].append(media['data-src'])
                            else:
                                company_data['company_photo'].append(media['data-src'])

        else:
            print('Error: {}, url: {}'.format(response.status_code, url))
            return {}

        # for k, v in company_data.items():
        #     print('{}: {}'.format(k, v))

        return company_data


    def email_decode(self, protected_email: str) -> str:
        r = int(protected_email[:2], 16)
        email = ''.join([chr(int(protected_email[i:i+2], 16) ^ r) for i in range(2, len(protected_email), 2)])
        return email


    def get_vacancy_date(self, str_date: str) -> dict:
        date_values = {}
        ru_month = {
            'января': '1',
            'февраля': '2',
            'марта': '3',
            'апреля': '4',
            'мая': '5',
            'июня': '6',
            'июля': '7',
            'августа': '8',
            'сентября': '9',
            'октября': '10',
            'ноября': '11',
            'декабря': '12',
        }
        print('str_date: {}'.format(str_date))
        list_date = str_date.split()
        print('list_date: ', list_date)
        datetime_now = datetime.datetime.now()

        if len(list_date) == 5:

            if list_date[2].isdigit() and int(list_date[2]) >= 1 and int(list_date[2]) <= 31:
                date_values['day'] = list_date[2]
            else:
                date_values['day'] = datetime_now.day

            if list_date[3] in ru_month:
                date_values['month'] = ru_month[list_date[3]]
            else:
                date_values['month'] = datetime_now.month

            if list_date[4].isdigit() and int(list_date[4]) > 0 and int(list_date[4]) < 2030:
                date_values['year'] = list_date[4]
            else:
                date_values['year'] = datetime_now.year

            print('date_values: ', date_values)

        else:
            date_values['day'] = datetime_now.day
            date_values['month'] = datetime_now.month
            date_values['year'] = datetime_now.year

        return date_values
