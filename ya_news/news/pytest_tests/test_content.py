from django.conf import settings

from news.forms import CommentForm


def test_news_count_on_home_page_is_limited(many_news, client, home_url):
    """На главной странице не больше установленного числа новостей."""
    response = client.get(home_url)

    assert 'object_list' in response.context
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_are_sorted_newest_first(many_news, client, home_url):
    """Новости на главной отсортированы от свежих к старым."""
    response = client.get(home_url)

    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [item.date for item in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_are_sorted_oldest_first(
    news,
    many_comments,
    client,
    detail_url,
):
    """Комментарии на странице новости отсортированы от старых к новым."""
    response = client.get(detail_url)

    assert 'news' in response.context
    all_comments = response.context['news'].comment_set.all()
    all_timestamps = [item.created for item in all_comments]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(news, client, detail_url):
    """Анонимному пользователю форма комментария не передаётся."""
    response = client.get(detail_url)

    assert 'form' not in response.context


def test_authorized_client_has_form(news, author_client, detail_url):
    """Авторизованный пользователь получает форму комментария."""
    response = author_client.get(detail_url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
