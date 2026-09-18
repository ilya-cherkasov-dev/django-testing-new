from datetime import timedelta

import pytest
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

HOME_PAGE_NEWS_LIMIT = 10
COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый текст комментария'
BAD_WORD_TEXT = 'Ты редиска, дружище!'
BAD_WORD_WARNING = 'Не ругайтесь!'


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def reader(django_user_model, db):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author, db):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, db):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Заголовок новости',
        text='Текст новости.',
    )


@pytest.fixture
def comment(news, author, db):
    return Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT,
    )


@pytest.fixture
def many_news(db):
    today = timezone.now().date()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости.',
            date=today - timedelta(days=(HOME_PAGE_NEWS_LIMIT - index)),
        )
        for index in range(HOME_PAGE_NEWS_LIMIT + 1)
    )


@pytest.fixture
def many_comments(news, author, db):
    now = timezone.now()
    comments = []
    for index in range(3):
        item = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        item.created = now - timedelta(minutes=index)
        item.save()
        comments.append(item)
    return comments


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))
