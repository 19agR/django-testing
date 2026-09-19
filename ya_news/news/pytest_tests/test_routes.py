from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture as lf


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'request_client, url, expected_status',
    (
        (lf('client'), lf('home_url'), HTTPStatus.OK),
        (lf('client'), lf('detail_url'), HTTPStatus.OK),
        (lf('author_client'), lf('edit_url'), HTTPStatus.OK),
        (lf('author_client'), lf('delete_url'), HTTPStatus.OK),
        (lf('user_client'), lf('edit_url'), HTTPStatus.NOT_FOUND),
        (lf('user_client'), lf('delete_url'), HTTPStatus.NOT_FOUND),
        (lf('client'), lf('signup_url'), HTTPStatus.OK),
        (lf('client'), lf('login_url'), HTTPStatus.OK),
    ),
)
def test_get_requests_have_expected_statuses(
        request_client,
        url,
        expected_status,
):
    response = request_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'request_client, url, expected_status',
    ((lf('client'), lf('logout_url'), HTTPStatus.OK),),
)
def test_post_requests_have_expected_statuses(
        request_client,
        url,
        expected_status,
):
    response = request_client.post(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('url', (lf('edit_url'), lf('delete_url')))
def test_anonymous_user_is_redirected_from_comment_pages(
        client,
        login_url,
        url,
):
    response = client.get(url)
    assert response.url == f'{login_url}?next={url}'
