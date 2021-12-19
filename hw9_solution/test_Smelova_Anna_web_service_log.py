import pytest
import requests
from task_Smelova_Anna_web_service_log import app, WIKI_BASE_SEARCH_URL, parse_article_count


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_parse_article_count(capsys):
    response = requests.get(WIKI_BASE_SEARCH_URL + "<bloomberg>" )
    assert 200 == response.status_code, (
        f'Wrong status code: {response.status_code}, '
        f'expected 200'
    )
    expected_result = 40350
    result = parse_article_count(response.text)
    assert expected_result <= result, (
        f'Wrong count: expected {expected_result}, '
        f"get {result}"
    )


def test_can_proxy_request_to_wiki(client):
    response = client.get('/api/search?query=python network')
    assert 200 == response.status_code, (
        f'Wrong status code: {response.status_code}, '
        f'expected 200'
    )
