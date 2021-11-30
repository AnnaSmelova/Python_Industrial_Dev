#!/usr/bin/env python3
"""
Module for Web Spy Gitlab
"""
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from lxml import html
import requests


URL_GITLAB_FEATURES = 'https://about.gitlab.com/features/'


def get_products_info_by_url(url=URL_GITLAB_FEATURES):
    """Count products from url function

    :param url: target url
    :return: products cnt divides by cost
    """
    response = requests.get(url)
    dom = html.fromstring(response.text)

    free_products_blocks = dom.xpath("//a[@title='Available in GitLab SaaS Free']")
    free_result = len(free_products_blocks)

    enterprise_products_blocks = dom.xpath("//a[@title='Not available in SaaS Free']")
    enterprise_result = len(enterprise_products_blocks)

    return free_result, enterprise_result


def get_products_info_by_html(html_data):
    """Count products from html function

    :param html_data: target html
    :return: products cnt divides by cost
    """
    html_data = html.fromstring(html_data)
    free_products_blocks = html_data.xpath("//a[@title='Available in GitLab SaaS Free']")
    free_result = len(free_products_blocks)

    enterprise_products_blocks = html_data.xpath("//a[@title='Not available in SaaS Free']")
    enterprise_result = len(enterprise_products_blocks)

    return free_result, enterprise_result


def callback_gitlab():
    """Callback function for query

    :param arguments: cmd arguments
    :return: nothing
    """
    free_result, enterprise_result = get_products_info_by_url(URL_GITLAB_FEATURES)
    print(f'free products: {free_result}', file=sys.stdout)
    print(f'enterprise products: {enterprise_result}', file=sys.stdout)


def setup_parser(parser):
    """Setup cmd parser arguments

    :param parser: parser for arguments
    :return: nothing
    """
    subparsers = parser.add_subparsers(help="choose command")

    gitlab_parser = subparsers.add_parser(
        "gitlab",
        help="web spy gitlab",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    gitlab_parser.set_defaults(callback=callback_gitlab)


def main():
    """Main function"""
    parser = ArgumentParser(
        prog='gitlab',
        description="Web Spy Gitlab",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback()


if __name__ == "__main__":
    main()
