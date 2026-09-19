from notes.forms import NoteForm

from .base import BaseTestCase


class TestContent(BaseTestCase):
    def test_author_note_is_in_notes_list_context(self):
        response = self.author_client.get(self.list_url)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note, response.context['object_list'])

    def test_other_users_notes_are_absent_from_notes_list(self):
        response = self.author_client.get(self.list_url)
        self.assertNotIn(self.other_note, response.context['object_list'])

    def test_note_form_is_passed_to_create_and_edit_pages(self):
        urls = (self.add_url, self.edit_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
