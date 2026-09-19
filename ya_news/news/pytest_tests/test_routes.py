from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url_fixture',
    ('home_url', 'detail_url', 'login_url', 'signup_url'),
)
def test_pages_available_to_anonymous_user(
    client,
    db,
    request,
    url_fixture,
):
    """Главная, новость, вход и регистрация доступны анониму."""
    url = request.getfixturevalue(url_fixture)

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_comment_pages_available_to_author(
    author_client,
    request,
    url_fixture,
):
    """Автору доступны редактирование и удаление своего комментария."""
    url = request.getfixturevalue(url_fixture)

    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_comment_pages_unavailable_to_reader(
    reader_client,
    request,
    url_fixture,
):
    """Другой пользователь получает 404 на страницах чужого комментария."""
    url = request.getfixturevalue(url_fixture)

    response = reader_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_anonymous_user_is_redirected_to_login(
    client,
    login_url,
    request,
    url_fixture,
):
    """Анонимный пользователь перенаправляется на страницу входа."""
    url = request.getfixturevalue(url_fixture)
    expected_url = f'{login_url}?next={url}'

    response = client.get(url)

    assertRedirects(response, expected_url)


def test_logout_accepts_post_request(author_client, logout_url):
    """Авторизованный пользователь выходит из аккаунта POST-запросом."""
    response = author_client.post(logout_url)

    assert response.status_code == HTTPStatus.OK
