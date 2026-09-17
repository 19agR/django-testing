from datetime import timedelta
from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News


pytestmark = pytest.mark.django_db


def test_home_page_contains_limited_number_of_news(client):
    news_count = settings.NEWS_COUNT_ON_HOME_PAGE
    today = timezone.now().date()
    News.objects.bulk_create([
        News(
            title=f'Новость {number}',
            text='Текст новости',
            date=today - timedelta(days=number),
        )
        for number in range(news_count + 1)
    ])

    response = client.get(reverse('news:home'))

    assert len(response.context['object_list']) == news_count


def test_news_on_home_page_are_sorted_from_new_to_old(client):
    today = timezone.now().date()
    expected_news = [
        News.objects.create(
            title=f'Новость {number}',
            text='Текст новости',
            date=today - timedelta(days=number),
        )
        for number in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]

    response = client.get(reverse('news:home'))

    assert list(response.context['object_list']) == expected_news


def test_comments_on_detail_page_are_sorted_from_old_to_new(
        client,
        author,
        news,
):
    now = timezone.now()
    expected_comments = []
    for number in range(3):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {number}',
        )
        Comment.objects.filter(pk=comment.pk).update(
            created=now + timedelta(minutes=number)
        )
        expected_comments.append(comment)
    url = reverse('news:detail', args=(news.pk,))

    response = client.get(url)

    comments = response.context['object'].comment_set.all()
    assert list(comments) == expected_comments


def test_anonymous_user_has_no_comment_form(client, news):
    response = client.get(reverse('news:detail', args=(news.pk,)))

    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


def test_authorized_user_has_comment_form(author_client, news):
    response = author_client.get(reverse('news:detail', args=(news.pk,)))

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.context['form'], CommentForm)
