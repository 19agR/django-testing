from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.note = Note.objects.create(
            title='Исходная заметка',
            text='Исходный текст',
            slug='source-note',
            author=cls.author,
        )
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.note_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note',
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_authorized_user_can_create_note(self):
        response = self.author_client.post(self.add_url, data=self.note_data)

        self.assertRedirects(response, self.success_url)
        self.assertTrue(
            Note.objects.filter(
                title=self.note_data['title'],
                text=self.note_data['text'],
                slug=self.note_data['slug'],
                author=self.author,
            ).exists()
        )

    def test_anonymous_user_cannot_create_note(self):
        notes_count = Note.objects.count()
        login_url = reverse('users:login')

        response = self.client.post(self.add_url, data=self.note_data)

        self.assertRedirects(response, f'{login_url}?next={self.add_url}')
        self.assertEqual(Note.objects.count(), notes_count)

    def test_note_slug_must_be_unique(self):
        note_data = self.note_data | {'slug': self.note.slug}

        response = self.author_client.post(self.add_url, data=note_data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response.context['form'],
            'slug',
            self.note.slug + WARNING,
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug_is_created_from_title(self):
        note_data = self.note_data | {'slug': ''}

        response = self.author_client.post(self.add_url, data=note_data)

        self.assertRedirects(response, self.success_url)
        created_note = Note.objects.get(title=note_data['title'])
        self.assertEqual(created_note.slug, slugify(note_data['title']))


class TestNoteEditingAndDeletion(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.other_user = User.objects.create_user(
            username='Другой пользователь'
        )
        cls.note = Note.objects.create(
            title='Исходная заметка',
            text='Исходный текст',
            slug='source-note',
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.updated_data = {
            'title': 'Обновлённая заметка',
            'text': 'Обновлённый текст',
            'slug': 'updated-note',
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.other_user_client = Client()
        self.other_user_client.force_login(self.other_user)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            self.edit_url,
            data=self.updated_data,
        )

        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.updated_data['title'])
        self.assertEqual(self.note.text, self.updated_data['text'])
        self.assertEqual(self.note.slug, self.updated_data['slug'])

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_url)

        self.assertRedirects(response, self.success_url)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_other_user_cannot_edit_note(self):
        response = self.other_user_client.post(
            self.edit_url,
            data=self.updated_data,
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Исходная заметка')
        self.assertEqual(self.note.text, 'Исходный текст')
        self.assertEqual(self.note.slug, 'source-note')

    def test_other_user_cannot_delete_note(self):
        response = self.other_user_client.post(self.delete_url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
