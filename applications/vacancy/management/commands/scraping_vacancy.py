import logging
from django.core.management.base import BaseCommand
from applications.vacancy.models import VacancySite, ScrapingLink
# from applications.vacancy.parser.work_ua import ParserWorkUa
# from applications.vacancy.parser.career_habr_com import ParserCareerHabrCom
from applications.vacancy.tasks import (career_habr_com_vacancy_scraping, work_ua_vacancy_scraping)


logger = logging.getLogger('parser')


class Command(BaseCommand):
    help = 'Scraping vacancies and companies. Usage example: python manage.py scraping_vacancy --website https://career.habr.com --skill python'

    def add_arguments(self, parser):
        parser.add_argument(
        '-w',
        '--website',
        action='store',
        # default='https://career.habr.com',
        help='Сайт для парсинга вакансий (например: https://career.habr.com)'
        )

        parser.add_argument(
        '-s',
        '--skill',
        action='store',
        # default='python',
        help='Навык для парсинга вакансий (например: python)'
        )

    def handle(self, *args, **options):
        scraping_website = ''
        # bot = ''
        url = ''

        if options['website']:
            scraping_website = VacancySite.objects.filter(link=options['website']).first()

            if scraping_website:

                if options['skill']:
                    url = ScrapingLink.objects.filter(scraping_site=scraping_website, skill=options['skill']).first()

                if url:
                    # if 'https://www.work.ua' in url.link:
                    #     bot = ParserWorkUa(None, options['skill'])
                    # elif 'https://career.habr.com' in url.link:
                    #     bot = ParserCareerHabrCom(None, options['skill'])

                    # if bot:
                    #     try:
                    #         bot.scraping()
                    #     except Exception as er:
                    #         error_msg = 'Scraping site: {0}, skill: {1} -> Finished Error: {2}'.format(
                    #             options['website'],
                    #             options['skill'],
                    #             er,
                    #         )
                    #         print(error_msg)
                    #         logger.error(error_msg)
                    # else:
                    #     warning_msg = 'С этими данными не удаётся запустить процесс скрапинга, scraping-link: {}, skill: {}'.format(
                    #         url.link,
                    #         options['skill'],
                    #     )
                    #     print(warning_msg)
                    #     logger.warning(warning_msg)

                    try:
                        if 'https://www.work.ua' in url.link:
                            work_ua_vacancy_scraping.delay(None, options['skill'])
                        elif 'https://career.habr.com' in url.link:
                            career_habr_com_vacancy_scraping.delay(None, options['skill'])
                    except Exception as er:
                        error_msg = 'Scraping site: {0}, skill: {1} -> Finished Error: {2}'.format(
                            options['website'],
                            options['skill'],
                            er,
                        )
                        print(error_msg)
                        logger.error(error_msg)

                else:
                    skills_qrs = ScrapingLink.objects.filter(scraping_site=scraping_website).values('skill')
                    skills_str = ', '.join([s['skill'] for s in skills_qrs if 'skill' in s])
                    info_msg = 'Скрапинг вакансий с саита "{}" доступен только по одному из таких навыков: {}'.format(
                        scraping_website.link,
                        skills_str,
                    )
                    print(info_msg)
                    logger.info(info_msg)

        if not scraping_website:
            websites_qrs = VacancySite.objects.all().values('link')
            websites_str = ', '.join([w['link'] for w in websites_qrs if 'link' in w])
            print(f'Для скрапинга вакансий нужно выбрать один из доступных веб-сайтов: {websites_str}. \nЧтобы узнать больше используйте опцию: --help')
