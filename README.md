# Django Project

## Russian

Приложение для скрапинга вакансий ИТ-специалистов с сайтов: work.ua и career.habr.com

Работоспособность проверялась с `Django==4.2.7` и `Python 3.12.1`

## Установка

```bash
# клонируем репозиторий
git clone https://github.com/o5b/django-scraping-vacancy.git
# переходим в папку проекта
cd django-scraping-vacancy/
# устанавливаем и активируем виртуальное окружение
python3.12 -m venv env
source env/bin/activate
# устанавливаем зависимости, если нужны только базовые пакеты:
pip install -r requirements/base.txt
# если нужны и базовые и пакеты разработчика:
pip install -r requirements/local.txt
```

![demo](doc/install_monokai.gif)

## Использование

### Запуск в докере контейнеров `redis` и `postgresql`

Для скрапинга будет использоваться `Celery` и в качестве брокера сообщений `Redis`.

При использовании с `Celery` бд `sqlite3` возможна ошибка `database is locked`. Чтобы избежать этого нужно установить `Postgresql`.

```bash
# переходим в папку:
cd django-scraping-vacancy/compose/
# запуск контейнеров с redis, postgresql и pgadmin4:
docker-compose -f docker-compose.yml up -d
# для остановки:
docker-compose -f docker-compose.yml down -v
```

![demo](doc/docker_monokai.gif)

### Подготовка перед первым использованием

В настройках `settings` нужно указать бд `postgresql` и подготовить перед первым использованием:

```bash
# переходим в папку проекта
cd django-scraping-vacancy/
# если ещё не активировали, то активируем виртуальное окружение
source env/bin/activate
# для создания базы данных
python manage.py migrate
# создаём суперпользователя для входа в админсайт Django
python manage.py createsuperuser
# собираем все статические файлы (.css, .js) в папку `static`
python manage.py collectstatic
# для поиска нужно запустить команду `haystack`
python manage.py rebuild_index
```

![demo](doc/init_monokai.gif)

### Запуск сервера

В отдельной консоли нужно запустить `Django`:

```bash
# переходим в папку проекта
cd django-scraping-vacancy/
# если ещё не активировали, то активируем виртуальное окружение
source env/bin/activate
# запуск сервера
python manage.py runserver localhost:8000
# сервер будет доступен по адрессу:   http://127.0.0.1:8000/
# админсайт:                          http://127.0.0.1:8000/admin/
```

![demo](doc/runserver_monokai.gif)

### Запуск Celery

В другой консоли запустим `Celery`:

```bash
# переходим в папку проекта
cd django-scraping-vacancy/
# если ещё не активировали, то активируем виртуальное окружение
source env/bin/activate
# команда для запуска Celery:
celery -A settings worker -l INFO
# для параллельного скрапинга, например с work.ua и хабр карьера,
# чтобы каждого бота обрабатывал свой Woker, предыдущую комманду нужно запускать с опцией `-O fair`:
celery -A settings worker -l INFO -O fair
```

![demo](doc/celery_monokai.gif)

<!-- ```bash
# для запуска задач по расписанию (которые создаются в админк, в разделе `ПЕРИОДИЧЕСКИЕ ЗАДАЧИ`)
# нужно помимо предыдущей команды, запустить в новой консоли следующую команду:
celery -A settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

![demo](doc/celery_beat_add_interval-peek.gif)
![demo](doc/celery_beat_add_periodic_task_peek.gif) -->

## Скрапинг вакансий

*На данный момент доступен скрапинг вакансии с таких сайтов:*
- https://www.work.ua
- https://career.habr.com

*В начале нужно добавить `сайт` и `ссылку для скрапинга` нужного навыка. Это можно сделать вручную через `админку` сайта (1) или загрузив нужные данные из папки `/fixtures` в базу данных (2).*

1. **Первый вариант - Ввод нужных данных через админку сайта**

```
В первую очередь добавляем сайт на странице: http://127.0.0.1:8000/admin/vacancy/vacancysource/
заполняем обязательное поле "Ссылка на сайт", например:
https://career.habr.com
или
https://www.work.ua
```

![demo](doc/add_site-peek.gif)

```
Затем добавляем ссылку для скрапинга нужного навыка на странице:
http://127.0.0.1:8000/admin/vacancy/scrapinglink/
Заполняем поля "Навык", "Ссылка для скрапинга" и "Скрапинг на сайте"
Например, для поиска вакансий по навыку "python"

для Хабр Карьера:
"Навык"                 - python
"Ссылка для скрапинга"  - https://career.habr.com/vacancies?q=python&sort=date&type=all
"Скрапинг на сайте"     - из списка выбираем: https://career.habr.com

для work.ua:
"Навык"                 - python
"Ссылка для скрапинга"  - https://www.work.ua/ru/jobs-python/
"Скрапинг на сайте"     - выбираем: https://www.work.ua
```

![demo](doc/add_web3_scraping_link-peek.gif)

2. **Второй вариант - Загрузка нужных данных в бд**

```bash
# переходим в папку проекта
cd django-scraping-vacancy/
# если ещё не запустили, то запускаем виртуальное окружение
source env/bin/activate
# загрузка данных в бд:
# если нужны только данные о сайтах (work.ua, career.habr.com) и навыках (python, web3)
# этого будет достаточно для начала скрапинга
python manage.py loaddata fixtures/vacancysite_vacancysource_db.json
# если нужны все данные приложения vacancy (сайты, навыки и немного вакансий) подойдёт для тестирования:
python manage.py loaddata fixtures/vacancy_full_db.json
```

![demo](doc/fixtures_monokai.gif)

### Запуск команды для скрапинга вакансий

```bash
# переходим в папку проекта
cd django-scraping-vacancy/
# если ещё не запустили, то запускаем виртуальное окружение
source env/bin/activate
# справка по команде скрапинга вакансий
python manage.py scraping_vacancy --help
# нужно указать сайт и навык, например
python manage.py scraping_vacancy --website https://career.habr.com --skill python
```

![demo](doc/scraping_command_monokai.gif)

В другой консоли должен быть запущен `celery`:

![demo](doc/scraping_command_celery_monokai.gif)

### Периодические задачи для Скрапинга

Создаём интервал:
![demo](doc/celery_beat_add_interval-peek.gif)
Создаём периодическую задачу:
![demo](doc/celery_beat_add_periodic_task_peek.gif)

```bash
# запускаем celery:
celery -A settings worker -l INFO -O fair
# в новой консоли нужно так же запустить celery-beat:
celery -A settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Скрапинг вакансий через сайт администратора

На сайте администратора `Главная › Вакансии › Ссылки для скрапинга ›`, на странице конкретной ссылки для скрапинга (например: http://127.0.0.1:8000/admin/vacancy/scrapinglink/1/change/), есть кнопка `Начать скрапинг` для скрапинга вакансий по этой конкретной ссылке. Ход процесса можно отслеживать в терминале.

![demo](doc/admin_scraping-peek.gif)

## Структура проекта

Рекомендуется установить `virtualenv` в папку `env` в корне проекта.

```
/applications - папка для приложений django
---/core      - для абстрактных классов и утилит
---/main      - основное приложение
---/vacancy   - приложение для скрапинга
------/parser - для парсеров
/compose      - для файлов docker-compose
/env          - папка для виртуального окружения
/fixtures     - тестовые данные для наполнения бд
/frontend     - папка для исходных файлов "фронтэнда"
---/images    - collectstatic перемещает файлы из этой папки в `/static/images/`
---/scripts   - collectstatic перемещает файлы из этой папки в `/static/scripts/`
---/styles    - collectstatic перемещает файлы из этой папки в `/static/styles/`
/logs         - для хранения логов
/media        - папка для медиа файлов
/requirements - устанавливаемые пакеты
---base.txt   - установка только базовых пакетов
---local.txt  - установка и базовых пакетов и специфических пакетов для разработки
/settings     - настройки django
/static       - сюда collectstatic собирает все статические файлы проекта
/templates    - общие файлы html
/tmp          - для временных файлов
```

## Информация о некоторых пакетах

- **django-haystack** *и* **whoosh** - *для организации поиска по текстовому содержимому*
- **beautifulsoup4** - *для извлечения информации с веб-страниц*
- **pytils** - *инструменты для работы с русскими строками (транслитерация, числительные словами, русские даты и т.д.)*
- **singlemodeladmin** - *для создания не более одной записи модели (например: "about")*
- **django-object-actions** - *для лёгкого добавления своего функционал на сайте администратора Django*
- **django-split-settings** - *для структурирования настроек Django по нескольким файлам и каталогам*
- **django-cleanup** - *автоматически удаляет не используемые медиа файлы*
- **django-import-export** - *добавление на сайте администратора импорта/экспорта данных разного формата*
- **johnnydep** - *отображает дерево зависимостей пакета Python (пример: johnnydep django-ckeditor)*
- **celery** - *это асинхронная очередь задач*
- **redis** - *для подключения к бд redis*
- **django-celery-results** - *для сохранения результатов выполнения задач*
- **django-celery-beat** - *для запуска периодических задач*
