from http import HTTPStatus

from news.models import Comment

from .conftest import (
    BAD_WORD_TEXT,
    BAD_WORD_WARNING,
    COMMENT_TEXT,
    NEW_COMMENT_TEXT,
)


def test_anonymous_user_cannot_create_comment(client, news, detail_url):
    comments_before = set(Comment.objects.values_list('pk', flat=True))

    response = client.post(detail_url, data={'text': COMMENT_TEXT})

    comments_after = set(Comment.objects.values_list('pk', flat=True))
    assert response.status_code == HTTPStatus.FOUND
    assert comments_after == comments_before


def test_author_can_create_comment(
    author,
    author_client,
    news,
    detail_url,
):
    existing_ids = set(Comment.objects.values_list('pk', flat=True))

    response = author_client.post(detail_url, data={'text': COMMENT_TEXT})

    created_comments = Comment.objects.exclude(pk__in=existing_ids)
    assert response.url == f'{detail_url}#comments'
    assert created_comments.count() == 1
    comment = created_comments.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_comment_with_bad_word_is_not_created(
    author_client,
    news,
    detail_url,
):
    comments_before = set(Comment.objects.values_list('pk', flat=True))

    response = author_client.post(
        detail_url, data={'text': BAD_WORD_TEXT},
    )

    form = response.context['form']
    assert form.errors['text'] == [BAD_WORD_WARNING]
    comments_after = set(Comment.objects.values_list('pk', flat=True))
    assert comments_after == comments_before


def test_author_can_edit_own_comment(
    comment,
    author,
    author_client,
    news,
    edit_url,
    detail_url,
):
    response = author_client.post(edit_url, data={'text': NEW_COMMENT_TEXT})

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert response.url == f'{detail_url}#comments'
    assert updated_comment.text == NEW_COMMENT_TEXT
    assert updated_comment.author == author
    assert updated_comment.news == news


def test_reader_cannot_edit_foreign_comment(
    comment,
    reader_client,
    edit_url,
):
    response = reader_client.post(edit_url, data={'text': NEW_COMMENT_TEXT})

    saved_comment = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert saved_comment.text == comment.text
    assert saved_comment.author == comment.author
    assert saved_comment.news == comment.news


def test_author_can_delete_own_comment(
    comment,
    author_client,
    delete_url,
    detail_url,
):
    response = author_client.post(delete_url)

    assert response.url == f'{detail_url}#comments'
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_reader_cannot_delete_foreign_comment(
    comment,
    reader_client,
    delete_url,
):
    response = reader_client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
