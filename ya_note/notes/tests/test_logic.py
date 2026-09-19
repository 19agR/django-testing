from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

from .base import BaseTestCase


class TestNoteCreation(BaseTestCase):
    def test_authorized_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(self.add_url, data=self.note_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        created_note = Note.objects.get()
        self.assertEqual(created_note.title, self.note_data['title'])
        self.assertEqual(created_note.text, self.note_data['text'])
        self.assertEqual(created_note.slug, self.note_data['slug'])
        self.assertEqual(created_note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        notes_count = Note.objects.count()
        response = self.client.post(self.add_url, data=self.note_data)
        self.assertRedirects(
            response,
            f'{self.login_url}?next={self.add_url}',
        )
        self.assertEqual(Note.objects.count(), notes_count)

    def test_note_slug_must_be_unique(self):
        notes_count = Note.objects.count()
        note_data = self.note_data | {'slug': self.note.slug}
        response = self.author_client.post(self.add_url, data=note_data)
        self.assertEqual(Note.objects.count(), notes_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response.context['form'],
            'slug',
            self.note.slug + WARNING,
        )

    def test_empty_slug_is_created_from_title(self):
        Note.objects.all().delete()
        note_data = self.note_data | {'slug': ''}
        response = self.author_client.post(self.add_url, data=note_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        created_note = Note.objects.get()
        self.assertEqual(created_note.slug, slugify(note_data['title']))


class TestNoteEditingAndDeletion(BaseTestCase):
    def test_author_can_edit_note(self):
        response = self.author_client.post(
            self.edit_url,
            data=self.updated_data,
        )
        self.assertRedirects(response, self.success_url)
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.title, self.updated_data['title'])
        self.assertEqual(updated_note.text, self.updated_data['text'])
        self.assertEqual(updated_note.slug, self.updated_data['slug'])
        self.assertEqual(updated_note.author, self.author)

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
        unchanged_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(unchanged_note.title, self.note.title)
        self.assertEqual(unchanged_note.text, self.note.text)
        self.assertEqual(unchanged_note.slug, self.note.slug)
        self.assertEqual(unchanged_note.author, self.note.author)

    def test_other_user_cannot_delete_note(self):
        response = self.other_user_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
