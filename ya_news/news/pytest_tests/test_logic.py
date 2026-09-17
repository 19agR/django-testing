from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cannot_create_comment(client, news):
    url = reverse('news:detail', args=(news.pk,))
    comments_count = Comment.objects.count()
    login_url = reverse('users:login')

    response = client.post(url, data={'text': 'Новый комментарий'})

    assert response.url == f'{login_url}?next={url}'
    assert Comment.objects.count() == comments_count


def test_authorized_user_can_create_comment(author_client, author, news):
    url = reverse('news:detail', args=(news.pk,))
    comment_text = 'Новый комментарий'

    response = author_client.post(url, data={'text': comment_text})

    assert response.url == f'{url}#comments'
    assert Comment.objects.filter(
        news=news,
        author=author,
        text=comment_text,
    ).exists()


def test_comment_with_bad_word_is_not_created(author_client, news):
    url = reverse('news:detail', args=(news.pk,))
    comments_count = Comment.objects.count()
    comment_text = f'Ты {BAD_WORDS[0]}!'

    response = author_client.post(url, data={'text': comment_text})

    assert response.status_code == HTTPStatus.OK
    assert WARNING in response.context['form'].errors['text']
    assert Comment.objects.count() == comments_count


def test_author_can_edit_comment(author_client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    updated_text = 'Обновлённый комментарий'
    detail_url = reverse('news:detail', args=(comment.news.pk,))

    response = author_client.post(url, data={'text': updated_text})

    assert response.url == f'{detail_url}#comments'
    comment.refresh_from_db()
    assert comment.text == updated_text


def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    detail_url = reverse('news:detail', args=(comment.news.pk,))

    response = author_client.post(url)

    assert response.url == f'{detail_url}#comments'
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.parametrize('url_name', ('news:edit', 'news:delete'))
def test_user_cannot_change_other_authors_comment(
        user_client,
        comment,
        url_name,
):
    url = reverse(url_name, args=(comment.pk,))
    original_text = comment.text

    response = user_client.post(url, data={'text': 'Новый текст'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_text
