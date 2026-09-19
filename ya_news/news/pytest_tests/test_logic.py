from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cannot_create_comment(
    client,
    news,
    detail_url,
    form_data,
):
    """Анонимный пользователь не может создать комментарий."""
    response = client.post(detail_url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_author_can_create_comment(
    author,
    author_client,
    news,
    detail_url,
    url_to_comments,
    form_data,
):
    """Авторизованный пользователь создаёт один комментарий к новости."""
    response = author_client.post(detail_url, data=form_data)

    assert response.url == url_to_comments
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('word', BAD_WORDS)
def test_comment_with_bad_word_is_not_created(
    author_client,
    news,
    detail_url,
    word,
):
    """Комментарий со стоп-словом не сохраняется и получает ошибку."""
    bad_words_data = {'text': f'Какой-то текст, {word}, ещё текст'}

    response = author_client.post(detail_url, data=bad_words_data)

    assert 'form' in response.context
    assertFormError(response.context['form'], 'text', WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_own_comment(
    comment,
    author,
    author_client,
    news,
    edit_url,
    url_to_comments,
    form_data,
):
    """Автор меняет текст своего комментария, не меняя автора и новость."""
    response = author_client.post(edit_url, data=form_data)

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert response.url == url_to_comments
    assert updated_comment.text == form_data['text']
    assert updated_comment.author == author
    assert updated_comment.news == news


def test_reader_cannot_edit_foreign_comment(
    comment,
    reader_client,
    edit_url,
    form_data,
):
    """Другой пользователь не может изменить чужой комментарий."""
    response = reader_client.post(edit_url, data=form_data)

    saved_comment = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert saved_comment.text == comment.text
    assert saved_comment.author == comment.author
    assert saved_comment.news == comment.news


def test_author_can_delete_own_comment(
    comment,
    author_client,
    delete_url,
    url_to_comments,
):
    """Автор может удалить свой комментарий."""
    response = author_client.post(delete_url)

    assert response.url == url_to_comments
    assert Comment.objects.count() == 0


def test_reader_cannot_delete_foreign_comment(
    comment,
    reader_client,
    delete_url,
):
    """Другой пользователь не может удалить чужой комментарий."""
    response = reader_client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
