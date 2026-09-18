from news.forms import CommentForm

from .conftest import HOME_PAGE_NEWS_LIMIT


def test_news_count_on_home_page_is_limited(many_news, client, home_url):
    response = client.get(home_url)

    object_list = response.context['object_list']
    assert len(object_list) == HOME_PAGE_NEWS_LIMIT


def test_news_are_sorted_newest_first(many_news, client, home_url):
    response = client.get(home_url)

    object_list = response.context['object_list']
    all_dates = [item.date for item in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_are_sorted_oldest_first(
    news,
    many_comments,
    client,
    detail_url,
):
    response = client.get(detail_url)

    all_comments = response.context['news'].comment_set.all()
    all_timestamps = [item.created for item in all_comments]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(news, client, detail_url):
    response = client.get(detail_url)

    assert 'form' not in response.context


def test_authorized_client_has_form(news, author_client, detail_url):
    response = author_client.get(detail_url)

    assert isinstance(response.context['form'], CommentForm)
