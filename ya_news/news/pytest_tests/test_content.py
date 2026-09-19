import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_home_page_contains_limited_number_of_news(
        client,
        home_url,
        news_list,
):
    response = client.get(home_url)
    assert response.context['object_list'].count() == (
        settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_on_home_page_are_sorted_from_new_to_old(
        client,
        home_url,
        news_list,
):
    response = client.get(home_url)
    news_on_page = response.context['object_list']
    assert list(news_on_page) == sorted(
        news_on_page,
        key=lambda news: news.date,
        reverse=True,
    )


def test_comments_on_detail_page_are_sorted_from_old_to_new(
        client,
        comments,
        detail_url,
):
    response = client.get(detail_url)
    comments_on_page = response.context['object'].comment_set.all()
    assert list(comments_on_page) == sorted(
        comments_on_page,
        key=lambda comment: comment.created,
    )


def test_anonymous_user_has_no_comment_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_user_has_comment_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
