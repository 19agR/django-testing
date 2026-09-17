from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.reader = User.objects.create_user(username='Читатель')
        cls.note = Note.objects.create(
            title='Заметка автора',
            text='Текст заметки',
            slug='author-note',
            author=cls.author,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

    def test_home_page_is_available_for_anonymous_user(self):
        response = self.client.get(reverse('notes:home'))

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_user_has_access_to_personal_pages(self):
        urls = (
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_has_access_to_note_pages(self):
        urls = (
            reverse('notes:detail', args=(self.note.slug,)),
            reverse('notes:edit', args=(self.note.slug,)),
            reverse('notes:delete', args=(self.note.slug,)),
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_other_user_cannot_access_note_pages(self):
        urls = (
            reverse('notes:detail', args=(self.note.slug,)),
            reverse('notes:edit', args=(self.note.slug,)),
            reverse('notes:delete', args=(self.note.slug,)),
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_user_is_redirected_from_private_pages(self):
        urls = (
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
            reverse('notes:detail', args=(self.note.slug,)),
            reverse('notes:edit', args=(self.note.slug,)),
            reverse('notes:delete', args=(self.note.slug,)),
        )
        login_url = reverse('users:login')

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f'{login_url}?next={url}')

    def test_auth_pages_are_available_for_everyone(self):
        routes = (
            (reverse('users:signup'), 'get'),
            (reverse('users:login'), 'get'),
            (reverse('users:logout'), 'post'),
        )

        for url, method in routes:
            with self.subTest(url=url):
                response = getattr(self.client, method)(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
