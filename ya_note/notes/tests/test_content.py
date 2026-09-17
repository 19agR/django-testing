from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.other_user = User.objects.create_user(
            username='Другой пользователь'
        )
        cls.author_note = Note.objects.create(
            title='Заметка автора',
            text='Текст автора',
            slug='author-note',
            author=cls.author,
        )
        cls.other_note = Note.objects.create(
            title='Чужая заметка',
            text='Чужой текст',
            slug='other-note',
            author=cls.other_user,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_author_note_is_in_notes_list_context(self):
        response = self.author_client.get(reverse('notes:list'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.author_note, response.context['object_list'])

    def test_other_users_notes_are_absent_from_notes_list(self):
        response = self.author_client.get(reverse('notes:list'))

        self.assertNotIn(self.other_note, response.context['object_list'])

    def test_note_form_is_passed_to_create_and_edit_pages(self):
        urls = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.author_note.slug,)),
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
