# yamdb_final
## Проект YaMDb собирает отзывы пользователей на различные произведения

Проект предоставляет API в виде REST-сервиса для YaMDb.

## Возможности

- Создавать и редактировать  отзывы
- Проставлять оценки
- Аутентификация через JWT

## Технологии

Проект использует:
- [Django](https://www.djangoproject.com/) -  свободный фреймворк для веб-приложений на языке Python
- [Django Rest Framework](https://www.django-rest-framework.org/) - гибкий и мощный фреймворк для построения Web API
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io) - плагин JSON Web Token аутентификации для Django REST Framework

## Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:n0n6m3/infra_sp2.git
cd infra_sp2/api_yamdb/infra/
```
Создать в .env-файл по шаблону
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=<имя базы данных>
POSTGRES_USER=<логин для подключения к базе данных>
POSTGRES_PASSWORD=<пароль для подключения к БД>
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
```
Собрать и запустить контейнеры
```
sudo docker-compose up -d --build
```
Выполнить миграции
```
sudo docker-compose exec web python manage.py migrate
```
Создать суперпользователя
```
sudo docker-compose exec web python manage.py createsuperuser
```
Собрать статику
```
sudo docker-compose exec web python manage.py collectstatic --no-input
```

## Загрузка тестовых данных
В проект включены тестовые данные (каталог static/data). Для их загрузки в базу небходимо выполнить:
```
sudo docker-compose exec web python3 manage.py loadtestdata
```

## Ресурсы API YaMDb

|Ресурс                             | Описание                      |
------------------------------------|-------------------------------|
|/api/v1/auth/                      | аутентификация                |
|/api/v1/users/                     | пользователи                  |
|/api/v1/titles/                    | произведения                  |
|/api/v1/categories/                | категории произведений        |
|/api/v1/genres/                    | жанры произведений            |
|/api/v1/reviews/                   | отзывы на произведения        |
|/api/v1/comments/                  | комментарии к отзывам         |


## License

MIT

![Статус](https://github.com/n0n3m6/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
