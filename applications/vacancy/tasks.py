from celery import shared_task
from applications.vacancy.parser.career_habr_com import ParserCareerHabrCom
from applications.vacancy.parser.work_ua import ParserWorkUa


@shared_task
def work_ua_vacancy_scraping(link_id=None, skill=None):
    bot = ParserWorkUa(link_id, skill)
    try:
        bot.scraping()
        print('Scraping from work.ua Finished SUCCESS (link_id: {0}, skill: {1})'.format(link_id, skill))
    except Exception as er:
        print('\n{}\nScraping for work.ua Finished Error (link_id: {}, skill: {}) \nError Msg: {}\n{}\n'.format(
            '*'*60, link_id, skill, er, '*'*60))


@shared_task
def career_habr_com_vacancy_scraping(link_id=None, skill=None):
    bot = ParserCareerHabrCom(link_id, skill)
    try:
        bot.scraping()
        print('Scraping for career.habr.com Finished SUCCESS (link_id: {0}, skill: {1})'.format(link_id, skill))
    except Exception as er:
        print('\n{}\nScraping for career.habr.com Finished Error (link_id: {}, skill: {}) \nError Msg: {}\n{}\n'.format(
            '*'*60, link_id, skill, er, '*'*60))
