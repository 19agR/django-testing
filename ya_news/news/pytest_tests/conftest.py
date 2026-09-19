from datetime import timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

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


@pytest.fixture
def news_list(db):
    today = timezone.now().date()
    return News.objects.bulk_create([
        News(
            title=f'Новость {number}',
            text='Текст новости',
            date=today - timedelta(days=number),
        )
        for number in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])


@pytest.fixture
def comments(author, news):
    now = timezone.now()
    for number in range(3):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {number}',
        )
        Comment.objects.filter(pk=comment.pk).update(
            created=now + timedelta(minutes=number)
        )


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')
