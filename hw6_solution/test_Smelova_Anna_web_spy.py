import pytest

from task_Smelova_Anna_web_spy import get_products_info_by_url, get_products_info_by_html

from unittest.mock import patch, MagicMock
import os


URL_GITLAB_FEATURES = 'https://about.gitlab.com/features/'
HTML_EXPECTED_OUTCOME = (351, 218)
DEFAULT_ENCODING = 'utf-8'
DEFAULT_STATUS_CODE = 200
HTML_GITLAB_FEATURES_PATH = 'gitlab_features.html'
HTML_GITLAB_FEATURES_EXPECTED_PATH = 'gitlab_features_expected.html'


@pytest.mark.slow
def test_get_products_info_by_html():
    with open(HTML_GITLAB_FEATURES_PATH, 'rb') as html_fin:
        content = html_fin.read()
        real_outcome = get_products_info_by_html(content)
        real_free, real_enterprise = real_outcome
        expected_free, expected_enterprise = HTML_EXPECTED_OUTCOME
        assert HTML_EXPECTED_OUTCOME == real_outcome, (
            f"expected free product count is {expected_free}, while you calculated {real_free}; expected enterprise "
            f"product count is {expected_enterprise}, while you calculated {real_enterprise}"
        )


def build_response_mock_from_content(content, encoding=DEFAULT_ENCODING, status_code=DEFAULT_STATUS_CODE):
    response = MagicMock(
        text=content,
        content=content,
        encoding=encoding,
        status_code=status_code,
    )
    return response


@patch('requests.get')
@pytest.mark.slow
def test_get_products_info_by_url(mock_requests_get):
    with open(HTML_GITLAB_FEATURES_PATH, 'r') as content_fin:
        content = content_fin.read()
        mock_requests_get.return_value = build_response_mock_from_content(content)
    real_outcome = get_products_info_by_url(URL_GITLAB_FEATURES)
    real_free, real_enterprise = real_outcome
    expected_free, expected_enterprise = HTML_EXPECTED_OUTCOME
    assert HTML_EXPECTED_OUTCOME == real_outcome, (
        f"expected free product count is {expected_free}, while you calculated {real_free}; expected enterprise "
        f"product count is {expected_enterprise}, while you calculated {real_enterprise}"
    )


@pytest.mark.integration_test
def test_products_info_by_url_changed():
    with open(HTML_GITLAB_FEATURES_EXPECTED_PATH, 'r') as expected_fin:
        expected_html = expected_fin.read()
    real_outcome = get_products_info_by_url(URL_GITLAB_FEATURES)
    real_free, real_enterprise = real_outcome
    expected_outcome = get_products_info_by_html(expected_html)
    expected_free, expected_enterprise = expected_outcome
    assert expected_outcome == real_outcome, (
        f"expected free product count is {expected_free}, while you calculated {real_free}; expected enterprise "
        f"product count is {expected_enterprise}, while you calculated {real_enterprise}"
    )


@pytest.mark.slow
def test_entrypoint():
    exit_status = os.system('python3 task_Smelova_Anna_web_spy.py -h')
    assert exit_status == 0
