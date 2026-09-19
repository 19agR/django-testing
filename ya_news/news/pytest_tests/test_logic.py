from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture as lf

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cannot_create_comment(client, detail_url, login_url):
    comments_count = Comment.objects.count()
    response = client.post(detail_url, data={'text': 'Новый комментарий'})
    assert response.url == f'{login_url}?next={detail_url}'
    assert Comment.objects.count() == comments_count


def test_authorized_user_can_create_comment(
        author_client,
        author,
        news,
        detail_url,
):
    Comment.objects.all().delete()
    comment_text = 'Новый комментарий'
    response = author_client.post(detail_url, data={'text': comment_text})
    assert response.url == f'{detail_url}#comments'
    assert Comment.objects.count() == 1
    created_comment = Comment.objects.get()
    assert created_comment.text == comment_text
    assert created_comment.author == author
    assert created_comment.news == news


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_bad_word_is_not_created(
        author_client,
        bad_word,
        detail_url,
):
    comments_count = Comment.objects.count()
    response = author_client.post(detail_url, data={'text': bad_word})
    assert Comment.objects.count() == comments_count
    assert response.status_code == HTTPStatus.OK
    assert WARNING in response.context['form'].errors['text']


def test_author_can_edit_comment(
        author_client,
        author,
        comment,
        detail_url,
        edit_url,
):
    updated_text = 'Обновлённый комментарий'
    response = author_client.post(edit_url, data={'text': updated_text})
    assert response.url == f'{detail_url}#comments'
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == updated_text
    assert updated_comment.author == author
    assert updated_comment.news == comment.news


def test_author_can_delete_comment(
        author_client, comment, delete_url, detail_url):
    response = author_client.post(delete_url)
    assert response.url == f'{detail_url}#comments'
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.parametrize('url', (lf('edit_url'), lf('delete_url')))
def test_user_cannot_change_other_authors_comment(
        user_client,
        comment,
        url,
):
    response = user_client.post(url, data={'text': 'Новый текст'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    unchanged_comment = Comment.objects.get(pk=comment.pk)
    assert unchanged_comment.text == comment.text
    assert unchanged_comment.author == comment.author
    assert unchanged_comment.news == comment.news
