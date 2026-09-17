import pytest
from django.test import Client

from news.models import Comment, News


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create_user(username='Автор')


@pytest.fixture
def user(django_user_model, db):
    return django_user_model.objects.create_user(username='Пользователь')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def user_client(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(title='Новость', text='Текст новости')


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
