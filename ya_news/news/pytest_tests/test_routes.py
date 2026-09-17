from http import HTTPStatus

import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_home_page_is_available_for_anonymous_user(client):
    response = client.get(reverse('news:home'))

    assert response.status_code == HTTPStatus.OK


def test_news_detail_page_is_available_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.pk,))

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name', ('news:edit', 'news:delete'))
def test_comment_pages_are_available_for_author(
        author_client,
        comment,
        url_name,
):
    url = reverse(url_name, args=(comment.pk,))

    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name', ('news:edit', 'news:delete'))
def test_anonymous_user_is_redirected_from_comment_pages(
        client,
        comment,
        url_name,
):
    url = reverse(url_name, args=(comment.pk,))
    login_url = reverse('users:login')

    response = client.get(url)

    assert response.url == f'{login_url}?next={url}'


@pytest.mark.parametrize('url_name', ('news:edit', 'news:delete'))
def test_user_cannot_access_other_authors_comment_pages(
        user_client,
        comment,
        url_name,
):
    url = reverse(url_name, args=(comment.pk,))

    response = user_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('url_name, method', (
    ('users:signup', 'get'),
    ('users:login', 'get'),
    ('users:logout', 'post'),
))
def test_auth_pages_are_available_for_anonymous_user(
        client,
        url_name,
        method,
):
    response = getattr(client, method)(reverse(url_name))

    assert response.status_code == HTTPStatus.OK
