from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:signup'),
)
def test_pages_available_to_anonymous_user(client, db, name):
    url = reverse(name)

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


def test_detail_page_available_to_anonymous_user(client, detail_url):
    response = client.get(detail_url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_comment_pages_available_to_author(author_client, comment, name):
    url = reverse(name, args=(comment.pk,))

    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_comment_pages_unavailable_to_reader(reader_client, comment, name):
    url = reverse(name, args=(comment.pk,))

    response = reader_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_anonymous_user_is_redirected_to_login(
    client,
    comment,
    login_url,
    name,
):
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


def test_logout_accepts_post_request(author_client, logout_url):
    response = author_client.post(logout_url)

    assert response.status_code == HTTPStatus.OK
    assert '_auth_user_id' not in author_client.session


def test_logout_rejects_get_request(client, db, logout_url):
    response = client.get(logout_url)

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
