#!/usr/bin/env python3
"""
Web service for Wiki with Logging
"""
import logging.config
import yaml

import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, jsonify, make_response, request, abort
from flask.logging import create_logger


logging.config.dictConfig(yaml.safe_load(
    """
    version: 1.0
    formatters:
        simple:
            format: "%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s"
            datefmt: "%Y%m%d_%H%M%S"
    handlers:
        stream_handler:
            class: logging.StreamHandler
            stream: ext://sys.stderr
            level: DEBUG
            formatter: simple
        file_handler:
            class: logging.FileHandler
            filename: wiki_search_app.log
            level: DEBUG
            formatter: simple
    _loggers:
        web_service:
            level: DEBUG
            propagate: False
            handlers:
                - stream_handler
                - file_handler
    root:
        level: DEBUG
        handlers:
            - stream_handler
            - file_handler
    """
))


app = Flask(__name__)
app.logger = create_logger(app)

WIKI_BASE_URL = "https://en.wikipedia.org"
WIKI_BASE_SEARCH_URL = f"{WIKI_BASE_URL}/w/index.php?search="


@app.errorhandler(404)
def page_not_found(e) -> Response:
    """
    404 error
    :return: response for 404 page
    """
    return make_response('This route is not found', 404)


@app.errorhandler(500)
def wiki_unavailable(e) -> Response:
    """
    503 error
    :return: response for 503 page
    """
    return make_response('Wikipedia Search Engine is unavailable', 503)


@app.route('/api/search')
def api_wiki_proxy_search():
    """Search API"""
    query = request.args.get('query', '')
    app.logger.debug('start processing query: %s', query)
    response = requests.get(WIKI_BASE_SEARCH_URL + query)
    if not response.ok:
        abort(503)
    article_count = parse_article_count(response.text)
    app.logger.info('found %s articles for query: %s', article_count, query)
    app.logger.debug('finish processing query: %s', query)
    return jsonify({
        'version': 1.0,
        'article_count': article_count,
    })


def parse_article_count(search_output):
    """Parse function"""
    parsed = BeautifulSoup(search_output, 'html.parser')
    div = parsed.find('div', attrs={'class': 'results-info'})
    if div is None:
        return 0
    result = int(div.findAll('strong')[-1].text.replace(',', ''))
    return result
