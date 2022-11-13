import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from reviews.models import (Category, Comment, Genre, Review, Title,
                            TitleGenre, User)

from api_yamdb.settings import BASE_DIR

DATA_FILES_DIR = os.path.join(BASE_DIR, 'static/data/')
DATA_FILES_LIST = (
    'users.csv',
    'category.csv',
    'titles.csv',
    'review.csv',
    'comments.csv',
    'genre.csv',
    'genre_title.csv'
)
DATA_IMPORT_ERROR = ('Ошибка при импорте файла! '
                     'Возможно данные эту таблицу уже импортированы.')


class Command(BaseCommand):
    help = 'Импорт набора тестовых данных для приложения Review'

    def check_files(self):
        for file in DATA_FILES_LIST:
            if file not in os.listdir(DATA_FILES_DIR):
                raise CommandError(
                    'Отсутсвует необходимый для импорта файл  {}!'.format(file)
                )
            self.stdout.write('  {}... '.format(file), ending='')
            self.stdout.write(self.style.SUCCESS('OK'))

    def import_users(self):
        self.stdout.write('  Импорт из users.csv... ', ending='')
        with open(os.path.join(DATA_FILES_DIR, 'users.csv'),
                  encoding='utf-8') as f:
            csv_dict = csv.DictReader(f)
            for line in csv_dict:
                try:
                    User.objects.create(**line)
                except IntegrityError:
                    raise CommandError(DATA_IMPORT_ERROR)
        self.stdout.write(self.style.SUCCESS('OK'))

    def import_category(self):
        self.stdout.write('  Импорт из category.csv... ', ending='')
        with open(os.path.join(DATA_FILES_DIR, 'category.csv'),
                  encoding='utf-8') as f:
            csv_dict = csv.DictReader(f)
            for line in csv_dict:
                try:
                    Category.objects.create(**line)
                except IntegrityError:
                    raise CommandError(DATA_IMPORT_ERROR)
        self.stdout.write(self.style.SUCCESS('OK'))

    def import_titles(self):
        self.stdout.write('  Импорт из titles.csv... ', ending='')
        with open(os.path.join(DATA_FILES_DIR, 'titles.csv'),
                  encoding='utf-8') as f:
            csv_dict = csv.DictReader(f)
            for line in csv_dict:
                line['category'] = Category.objects.get(pk=line['category'])
                try:
                    Title.objects.create(**line)
                except IntegrityError:
                    raise CommandError(DATA_IMPORT_ERROR)
        self.stdout.write(self.style.SUCCESS('OK'))

    def import_reviews(self):
        self.stdout.write('  Импорт из review.csv... ', ending='')
        with open(os.path.join(DATA_FILES_DIR, 'review.csv'),
                  encoding='utf-8') as f:
            csv_dict = csv.DictReader(f)
            for line in csv_dict:
                line['author'] = User.objects.get(pk=line['author'])
                line['title'] = Title.objects.get(pk=line['title_id'])
                try:
                    Review.objects.create(**line)
                except IntegrityError:
                    raise CommandError(DATA_IMPORT_ERROR)
        self.stdout.write(self.style.SUCCESS('OK'))

    def import_comments(self):
        self.stdout.write('  Импорт из comments.csv... ', ending='')
        with open(os.path.join(DATA_FILES_DIR, 'comments.csv'),
                  encoding='utf-8') as f:
            csv_dict = csv.DictReader(f)
            for line in csv_dict:
                line['author'] = User.objects.get(pk=line['author'])
                line['review'] = Review.objects.get(pk=line['review_id'])
                try:
                    Comment.objects.create(**line)
                except IntegrityError:
                    raise CommandError(DATA_IMPORT_ERROR)
        self.stdout.write(self.style.SUCCESS('OK'))

    def import_genre(self):
        self.stdout.write('  Импорт из genre.csv... ', ending='')
        with open(os.path.join(DATA_FILES_DIR, 'genre.csv'),
                  encoding='utf-8') as f:
            csv_dict = csv.DictReader(f)
            for line in csv_dict:
                try:
                    Genre.objects.create(**line)
                except IntegrityError:
                    raise CommandError(DATA_IMPORT_ERROR)
        self.stdout.write(self.style.SUCCESS('OK'))

    def import_genre_title(self):
        self.stdout.write('  Импорт из genre_title.csv... ', ending='')
        with open(os.path.join(DATA_FILES_DIR, 'genre_title.csv'),
                  encoding='utf-8') as f:
            csv_dict = csv.DictReader(f)
            for line in csv_dict:
                try:
                    TitleGenre.objects.create(
                        title=Title.objects.get(pk=line['title_id']),
                        genre=Genre.objects.get(pk=line['genre_id'])
                    )
                except IntegrityError:
                    raise CommandError(DATA_IMPORT_ERROR)
        self.stdout.write(self.style.SUCCESS('OK'))

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(
            'Проверка наличия файлов в каталоге static/data/:'
        ))
        self.check_files()
        self.stdout.write(self.style.MIGRATE_HEADING(
            'Импорт данных из файлов:'
        ))
        self.import_users()
        self.import_category()
        self.import_titles()
        self.import_reviews()
        self.import_comments()
        self.import_genre()
        self.import_genre_title()
