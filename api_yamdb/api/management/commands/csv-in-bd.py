import csv
from django.db import connection
from django.core.management.base import BaseCommand

from api_yamdb.settings import BASE_DIR
from reviews.models import Category, Genre, Title, Review, Comment
from users.models import User


path = str(BASE_DIR / 'static/data/')
models = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    help = 'Команда для автоматического наполнения базы данных'

    def handle(self, *args, **options):
        self.all_models(self, *args)
        self.reviews_title_genre(self, *args)

    def all_models(self, *args):
        for model, csv_file in models.items():
            with open(path + '/' + csv_file, 'r', encoding='utf-8') as file:
                try:
                    rows = csv.DictReader(file)
                    records = [model(**row) for row in rows]
                    model.objects.bulk_create(records)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'База заполнена (модель {model.__name__})'
                        )
                    )
                except Exception as error:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Ошибка {error} при записи {model.__name__}'
                        )
                    )

    def reviews_title_genre(self, *args):
        with open(path + '/genre_title.csv', 'r', encoding='utf-8') as file:
            try:
                rows = csv.reader(file)
                records = [tuple(row) for row in rows][1:]
                with connection.cursor() as cur:
                    cur.executemany(
                        'INSERT INTO reviews_title_genre VALUES (%s, %s, %s)',
                        records
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            'База заполнена (reviews_title_genre)'
                        )
                    )
            except Exception as error:
                self.stdout.write(
                    self.style.ERROR(
                        f'Ошибка {error} при записи из genre_title.csv'
                    )
                )
