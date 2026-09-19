from http import HTTPStatus

from .base import BaseTestCase


class TestRoutes(BaseTestCase):
    def test_get_requests_have_expected_statuses(self):
        test_cases = (
            (self.client, self.home_url, HTTPStatus.OK),
            (self.author_client, self.list_url, HTTPStatus.OK),
            (self.author_client, self.success_url, HTTPStatus.OK),
            (self.author_client, self.add_url, HTTPStatus.OK),
            (self.author_client, self.detail_url, HTTPStatus.OK),
            (self.author_client, self.edit_url, HTTPStatus.OK),
            (self.author_client, self.delete_url, HTTPStatus.OK),
            (self.other_user_client, self.detail_url, HTTPStatus.NOT_FOUND),
            (self.other_user_client, self.edit_url, HTTPStatus.NOT_FOUND),
            (self.other_user_client, self.delete_url, HTTPStatus.NOT_FOUND),
            (self.client, self.signup_url, HTTPStatus.OK),
            (self.client, self.login_url, HTTPStatus.OK),
        )
        for client, url, expected_status in test_cases:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_post_requests_have_expected_statuses(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_user_is_redirected_from_private_pages(self):
        urls = (
            self.list_url,
            self.success_url,
            self.add_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f'{self.login_url}?next={url}')
