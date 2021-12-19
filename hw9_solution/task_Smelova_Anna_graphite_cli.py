#!/usr/bin/env python3
"""
Graphite CLI to handle Logging
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import List
from datetime import datetime
import time

DEFAULT_DATASET_PATH = 'wiki_search_app.log'
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = '2003'


def get_answer_data(parsed_logs: List) -> tuple:
    """Get Answer Data function"""
    article_found = 0
    start, finish = 0, 0
    for log in parsed_logs:
        if log[0] == 'start':
            start = log[1]
        elif log[0] == 'finish':
            finish = log[1]
        elif log[0] == 'found':
            article_found = log[2]
    delta = (finish - start).total_seconds()
    finish_u = int(time.mktime(finish.timetuple()))

    return article_found, delta, finish_u


def parse_log(row: str):
    """Parse Log function"""
    line = row.split()
    parsed = [line[3]]

    date_time_obj = datetime.strptime(line[0], "%Y%m%d_%H%M%S.%f")
    parsed.append(date_time_obj)

    if line[2] == 'INFO':
        query = ''.join(line[8:])
        parsed.append(line[4])
    else:
        query = ''.join(line[6:])

    return query, parsed


def print_response(result: tuple, host: str, port: int):
    """Print Response function"""
    print(f'echo "wiki_search.article_found {result[0]} {result[2]}" | nc -N {host} {port}')
    print(f'echo "wiki_search.complexity {result[1]:.3f} {result[2]}" | nc -N {host} {port}')


def configure_response(process, host, port):
    """Configure Response function"""
    logs = {}
    with open(process, 'r', encoding='utf-8') as fin:
        data = fin.readlines()
    for line in data:
        query, parsed = parse_log(line)
        logs.setdefault(query, []).append(parsed)
        if len(logs[query]) == 3:
            result = get_answer_data(logs[query])
            print_response(result, host, port)
            del logs[query]


def process_arguments(arguments):
    """Process function"""
    configure_response(arguments.process, arguments.host, arguments.port)


def setup_parser(parser):
    """Setup cmd parser arguments

    :param parser: parser for arguments
    :return: nothing
    """
    parser.add_argument(
        "--process",
        default=DEFAULT_DATASET_PATH,
        required=True,
        help="path to log file default is %(default)s",
    )

    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        required=True,
        help="host default is %(default)s",
    )

    parser.add_argument(
        "--port",
        default=DEFAULT_PORT,
        required=True,
        help="port default is %(default)s",
    )

    parser.set_defaults(callback=process_arguments)


def main():
    """Main function"""
    parser = ArgumentParser(
        prog='graphite_cli',
        description='Graphite Cli',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()
