import random
import time
import datetime
import pytz

import requests
from bs4 import BeautifulSoup
from django.utils.text import slugify
import pytils

from applications.vacancy.models import Company, ScrapingLink, Vacancy, VacancySite

class ParserCareerHabrCom:
    """ Для получения вакансий и компаний с сайта career.habr.com """

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
        scraping_site_obj = VacancySite.objects.get(link='https://career.habr.com')

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
                latest_vacancy.vacancy_id,
                latest_vacancy.title,
                latest_vacancy.datetime.astimezone(pytz.timezone('Europe/Moscow'))
                )
            )

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
                    vacancies_from_current_page = soup.find_all('div', class_='vacancy-card__inner')

                    if vacancies_from_current_page:
                        print('############## page ############# vacancy count: ', len(vacancies_from_current_page))

                        for data in vacancies_from_current_page:
                            company = ''
                            vacancy_link = ''
                            vacancy_card_title = data.find('div', class_='vacancy-card__title')

                            if vacancy_card_title:
                                vacancy_title_a = vacancy_card_title.find('a', class_='vacancy-card__title-link')
                                vacancy_link = vacancy_title_a['href'] if 'href' in vacancy_title_a.attrs else ''
                                print('vacancy_link: ', vacancy_link)

                            if vacancy_link:
                                vacancy_id = vacancy_link.split("/")[2]

                                if vacancy_id.isdigit() and (vacancy_id not in vacancies_list):
                                    vacancies_list.append(vacancy_id)
                                    print('vacancies_list: ', len(vacancies_list))
                                    time.sleep(random.randint(2, 3))
                                    vacancy_data = self.vacancy(vacancy_id)

                                    if vacancy_data:
                                        datetime_now = datetime.datetime.now()

                                        if not vacancy_data['datetime']:
                                            vacancy_data['datetime'] = pytils.dt.ru_strftime(
                                                '%Y-%m-%dT%H:%M:%S%z+0300',  # +0300 Мск
                                                inflected=True,
                                                date=datetime_now
                                            )

                                        vacancy_datetime = datetime.datetime.strptime(vacancy_data['datetime'], '%Y-%m-%dT%H:%M:%S%z')

                                        print("vacancy_data['text_date']: {} ==> vacancy_datetime: {}".format(
                                            vacancy_data['text_date'], vacancy_datetime))

                                        if latest_vacancy:
                                            print('latest_vacancy.datetime.astimezone(pytz.timezone("Europe/Moscow")): {} >= vacancy_datetime: {} ===>>> {}'.format(
                                                latest_vacancy.datetime.astimezone(pytz.timezone('Europe/Moscow')),
                                                vacancy_datetime,
                                                latest_vacancy.datetime.astimezone(pytz.timezone('Europe/Moscow')) >= vacancy_datetime
                                                )
                                            )

                                            if latest_vacancy.datetime.astimezone(pytz.timezone('Europe/Moscow')) >= vacancy_datetime:
                                                scraping_stop = True
                                                break

                                        company_link = vacancy_data['company_link']
                                        print('company_link: ', company_link)

                                        if company_link not in companies_list:
                                            companies_list.append(company_link)
                                            print('companies_list: ', len(companies_list))

                                            time.sleep(random.randint(2, 3))
                                            company_data = self.company(company_link)

                                            if company_data:
                                                company, company_created = Company.objects.update_or_create(
                                                    company_id=company_link,
                                                    defaults={
                                                        'name': company_data['company_name'],
                                                        'slug': slugify(pytils.translit.slugify(company_data['company_name'][:50])),
                                                        'about': company_data['about_company'],
                                                        'employees': company_data['employees'],
                                                        'website': company_data['company_site'],
                                                        'company_id': company_link,
                                                        'about_short': company_data['company_about'],
                                                        'skills': company_data['user_skills'],
                                                        'company_ratings': company_data['company_ratings'],
                                                        'rating': company_data['rating'],
                                                        'statistics': company_data['statistics'],
                                                        'addresses': company_data['company_addresses'],
                                                        'contacts': company_data['contacts'],
                                                        'links': company_data['links'],
                                                        'members': company_data['company_public_members'],
                                                        'photo': company_data['company_photos'],
                                                        'video': '',
                                                        'scraping_site': scraping_site_obj,
                                                    },
                                                )

                                        elif (company_link in companies_list) or not company_data:
                                            company = Company.objects.filter(company_id=company_link).first()

                                        vacancy_slug = '{0}-{1}-{2}'.format(
                                            vacancy_id,
                                            company.slug if company else '',
                                            slugify(pytils.translit.slugify(vacancy_data['title'][:50]))
                                        )

                                        vacancy, vacancy_created = Vacancy.objects.update_or_create(
                                            vacancy_id=vacancy_id,
                                            defaults={
                                                'title': vacancy_data['title'],
                                                'slug': vacancy_slug,
                                                'body': vacancy_data['description'],
                                                'text_date': vacancy_data['text_date'],
                                                'datetime': vacancy_datetime if vacancy_datetime else datetime_now,
                                                'salary': vacancy_data['salary'],
                                                'address': vacancy_data['address_and_kind'],
                                                'requirements': vacancy_data['requirements'],
                                                'company': company if company else '',
                                                'vacancy_id': vacancy_id,
                                                'scraping_site': scraping_site_obj,
                                                'scraping_link': scraping_link_obj,
                                            }
                                        )

                                print('--------------------------')

                    next_page = soup.find('a', class_='next_page')
                    if next_page and ('href' in next_page.attrs):
                        url = 'https://career.habr.com{}'.format(next_page["href"])
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
            'requirements': '',
            'address_and_kind': '',
            'description': '',
            'company_title': '',
            'company_sub_title': '',
            'company_link': '',
            'company_website': '',
        }

        url = f"https://career.habr.com/vacancies/{vacancy_id}"
        response = requests.get(url, headers=self.get_user_agent())

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            if soup:
                basic_section = soup.find_all('div', class_='basic-section')

                if basic_section[0]:
                    title = basic_section[0].find('h1', class_='page-title__title')

                    if title:
                        vacancy_data["title"] = title.get_text().strip()

                    date = basic_section[0].find('time', class_='basic-date')
                    if date:
                        vacancy_data['text_date'] = date.get_text().strip()
                        vacancy_data['datetime'] = date['datetime'] if 'datetime' in date.attrs else ''

                    content_section_all = basic_section[0].find_all('div', class_='content-section')
                    for content_section in content_section_all:
                        content_section_h2 = content_section.find('h2', class_='content-section__title')
                        if content_section_h2:
                            content_section_h2_text = content_section_h2.get_text().strip()
                            if content_section_h2_text == 'Зарплата':
                                salary = content_section.find('div', class_='basic-salary basic-salary--appearance-vacancy-header')
                                if salary:
                                    vacancy_data['salary'] = salary.get_text().strip()
                            elif content_section_h2_text == 'Требования':
                                content_section_span = content_section.find('span', class_='inline-list')
                                if content_section_span:
                                    vacancy_data['requirements'] = content_section_span.get_text().strip()
                            elif content_section_h2_text == 'Местоположение и тип занятости':
                                content_section_span = content_section.find('span', class_='inline-list')
                                if content_section_span:
                                    vacancy_data['address_and_kind'] = content_section_span.get_text().strip()
                            elif content_section_h2_text == 'Компания':
                                vacancy_company_title = content_section.find('div', class_='vacancy-company__title')
                                if vacancy_company_title:
                                    vacancy_company_a = vacancy_company_title.find('a', class_='link-comp link-comp--appearance-dark')
                                    if vacancy_company_a:
                                        vacancy_data['company_title'] = vacancy_company_a.get_text().strip()
                                        vacancy_data['company_link'] = vacancy_company_a['href'] if 'href' in vacancy_company_a.attrs else ''
                                vacancy_company_sub_title = content_section.find('div', class_='vacancy-company__sub-title')
                                if vacancy_company_sub_title:
                                    vacancy_data['company_sub_title'] = vacancy_company_sub_title.get_text().strip()
                                vacancy_company_footer = content_section.find('div', class_='vacancy-company__footer')
                                if vacancy_company_footer:
                                    vacancy_company_website = vacancy_company_footer.find('a', class_='link-comp')
                                    if vacancy_company_website and 'target' in vacancy_company_website.attrs and vacancy_company_website['target'] == '_blank':
                                        vacancy_data['company_website'] = vacancy_company_website.get_text().strip()

                if basic_section[1]:
                    vacancy_description = basic_section[1].find('div', class_='vacancy-description__text')
                    if vacancy_description:
                        vacancy_description_str = '{}'.format(vacancy_description)
                        vacancy_description_str = vacancy_description_str.replace('<div class="vacancy-description__text">', '')
                        vacancy_description_str = vacancy_description_str.replace('<div class="style-ugc">', '')
                        vacancy_description_str = vacancy_description_str.replace('</div>', '')
                        vacancy_data['description'] = vacancy_description_str

        else:
            print('Error: {}, url: {}'.format(response.status_code, url))

        return vacancy_data


    def company(self, company_link: str) -> dict:
        company_data = {
            'about_company': '',
            'user_skills': '',
            'company_ratings': '',
            'company_name': '',
            'company_about': '',
            'company_site': '',
            'rating': '',
            'statistics': '',
            'company_addresses': '',
            'employees': '',
            'contacts': '',
            'links': '',
            'company_public_members': [],
            'company_photos': [],
        }

        url = f"https://career.habr.com{company_link}"
        print('url: ', url)
        response = requests.get(url, headers=self.get_user_agent())

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            if soup:
                content_main = soup.find('div', class_='content-wrapper__main content-wrapper__main--right')

                if content_main:
                    about_company = content_main.find('div', class_='about_company')

                    if about_company:
                        about_company_str = '{}'.format(about_company)
                        about_company_str = about_company_str.replace('<div class="about_company">', '')
                        about_company_str = about_company_str.replace('<div class="description">', '')
                        about_company_str = about_company_str.replace('</div>', '')
                        company_data['about_company'] = about_company_str

                    user_skills_list = content_main.find('div', class_='user_skills_list')
                    if user_skills_list:
                        company_data['user_skills'] = user_skills_list.get_text().strip()

                    company_ratings_section = content_main.find('div', class_='section section--company-rating company_ratings_section')
                    if company_ratings_section:
                        company_ratings = company_ratings_section.find('div', 'company_ratings_data')
                        if company_ratings:
                            company_data['company_ratings'] = company_ratings.get_text().strip()

                    company_photos_div = content_main.find(id='company_photos')
                    if company_photos_div:
                        company_photos_img = company_photos_div.find_all('img')
                        if company_photos_img:
                            for img in company_photos_img:
                                company_data['company_photos'].append(img['src'])

                content_sidebar = soup.find('aside', class_='content-wrapper__sidebar content-wrapper__sidebar--left')
                if content_sidebar:

                    company_name_div = content_sidebar.find('div', class_='company_name')
                    if company_name_div:
                        company_name_a = company_name_div.find('a')
                        if company_name_a:
                            company_data['company_name'] = company_name_a.get_text().strip()

                    company_about = content_sidebar.find('div', class_='company_about')
                    if company_about:
                        company_data['company_about'] = company_about.get_text().strip()

                    company_site_div = content_sidebar.find('div', class_='company_site')
                    if company_site_div:
                        company_site_a = company_site_div.find('a')
                        if company_site_a:
                            company_data['company_site'] = company_site_a['href']

                    company_score = content_sidebar.find('div', class_='company_name company_score')
                    if company_score:
                        rating = company_score.find('span', class_='rating')
                        company_data['rating'] = rating.get_text().strip()

                    statistics_all = content_sidebar.find_all('div', class_='statistics')
                    for statistics in statistics_all:
                        stat = ''
                        statistics_label = statistics.find('div', class_='label')
                        if statistics_label:
                            stat = statistics_label.get_text().strip()
                        statistics_count = statistics.find('div', class_='count')
                        if statistics_count:
                            stat += ': {}'.format(statistics_count.get_text().strip())
                        company_data['statistics'] += '; {}'.format(stat)

                    about_comp = content_sidebar.find('div', class_='about_comp')
                    if about_comp:

                        addresses = about_comp.find_all('div', class_='address')
                        for address in addresses:
                            company_data['company_addresses'] += '{}; '.format(address.get_text().strip())

                        employees = about_comp.find('div', class_='employees')
                        if employees:
                            company_data['employees'] = employees.get_text().strip()

                        contacts = about_comp.find_all('div', class_='contact')
                        for contact in contacts:
                            contact_str = ''
                            contact_type = contact.find('div', class_='type')
                            if contact_type:
                                contact_str = contact_type.get_text().strip()
                            contact_value = contact.find('div', class_='value')
                            if contact_value:
                                contact_str += ' {}'.format(contact_value.get_text().strip())
                            company_data['contacts'] += '{}; '.format(contact_str)

                        links = about_comp.find_all('div', class_='link')
                        for link in links:
                            link_a = link.find('a')
                            if link_a:
                                company_data['links'] += '{}; '.format(link_a['href'])

                        company_public_members = about_comp.find_all('a', class_='company_public_member')
                        for member in company_public_members:
                            member_dict = {}
                            member_dict['link'] = member['href']
                            avatar = member.find('img')
                            if avatar:
                                member_dict['avatar'] = avatar['src']
                            username = member.find('div', class_='username')
                            if username:
                                member_dict['username'] = username.get_text().strip()
                            position = member.find('div', class_='position')
                            if position:
                                member_dict['position'] = position.get_text().strip()
                            company_data['company_public_members'].append(member_dict)

        else:
            print('Error: {}, url: {}'.format(response.status_code, url))

        return company_data
