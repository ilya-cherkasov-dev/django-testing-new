from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


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
        text='Текст комментария',
    )


@pytest.fixture
def many_news(db):
    today = timezone.now().date()
    news_count = settings.NEWS_COUNT_ON_HOME_PAGE
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости.',
            date=today - timedelta(days=(news_count - index)),
        )
        for index in range(news_count + 1)
    )


@pytest.fixture
def many_comments(news, author, db):
    now = timezone.now()
    for index in range(3):
        item = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        item.created = now - timedelta(minutes=index)
        item.save()


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
def url_to_comments(detail_url):
    return f'{detail_url}#comments'


@pytest.fixture
def form_data():
    return {'text': 'Новый текст комментария'}


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))
