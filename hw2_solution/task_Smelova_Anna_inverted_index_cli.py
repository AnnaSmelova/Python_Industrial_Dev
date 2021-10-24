#!/usr/bin/env python3
"""
Module for Inverted Index library
"""
from __future__ import annotations
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import json
import re
from typing import Dict, List
from collections import defaultdict

DEFAULT_DUMP_STRATEGY = 'json'


class InvertedIndex:
    """
    Class for Inverted Index
    Provides search words, load and dump docs
    """

    def __init__(self, index_dict: Dict[str, List[int]]) -> None:
        """Class constructor

        :param index_dict: Dict[str, List[int]] - dict: keys:terms and values:lists of docs ids
        """
        self.index_dict = index_dict

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query

        :param words: List[str] - list of words
        :return: List[int] - list of docs ids which include ALL words from query
        """
        result_of_query = []
        if words:
            current_set = None
            for word in words:
                if word in self.index_dict.keys():
                    if current_set is None:
                        current_set = set(self.index_dict[word])
                    else:
                        current_set.intersection_update(set(self.index_dict[word]))
                else:
                    return []
            result_of_query = list(current_set)
        return result_of_query

    def dump(self, filepath: str, strategy='') -> None:
        """Convert index_dict into string and stores it in json and write it to filepath

        :param filepath: str - filepath to write
        :param strategy: str - strategy to store: json or pickle
        :return: nothing
        """
        strategy = strategy or 'json'
        if strategy == 'json':
            json_string = json.dumps(self.index_dict)
            with open(filepath, mode='w', encoding='utf8') as fout:
                fout.write(json_string)
        else:
            # TODO Realize pickle method
            pass

    @classmethod
    def load(cls, filepath: str) -> InvertedIndex:
        """Upload InvertedIndex from file by filepath

        :param filepath: str - filepath to upload json_string
        :return: InvertedIndex - InvertedIndex object
        """
        loaded_json_string = {}
        with open(filepath, mode='r', encoding='utf8') as fin:
            loaded_json_string = json.load(fin)
        inverted_index = InvertedIndex(loaded_json_string)
        return inverted_index

    def __repr__(self):
        repr_ = f'{self.__class__.__name__}(index_dict={self.index_dict})'
        return repr_

    def __eq__(self, rhs):
        outcome = (
                self.index_dict == rhs.index_dict
        )
        return outcome


def load_documents(filepath: str) -> defaultdict:
    """Upload Documents from file by filepath

    :param filepath: str - filepath to upload docs
    :return: Dict[int, str] - dictionary of documents in format id: str
    """
    print(f'Loading documents from {filepath} to build inverted index...', file=sys.stderr)
    documents_dict = defaultdict(list)
    with open(filepath, mode='r', encoding='utf8') as fin:
        for line in fin:
            doc_id, content = line.lower().strip().split("\t", 1)
            doc_id = int(doc_id)
            documents_dict[doc_id] = content
    return documents_dict


def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """Build inverted index from documents_dict

    :param documents: Dict[int, str] - dictionary of documents in format id: str
    :return: InvertedIndex - InvertedIndex object
    """
    print('Building inverted index for provided documents...', file=sys.stderr)
    index_dict = defaultdict(list)
    for doc_id, content in documents.items():
        words = re.split(r"\W+", content)
        for word in words:
            if doc_id not in index_dict[word]:
                index_dict[word].append(doc_id)
    return InvertedIndex(index_dict=index_dict)


def callback_build(arguments):
    """Callback function for build

    :param arguments: cmd arguments
    :return: nothing
    """
    documents = load_documents(arguments.path_to_load)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(arguments.path_to_store, arguments.dump_strategy)


def callback_query(arguments):
    """Callback function for query

    :param arguments: cmd arguments
    :return: nothing
    """
    inverted_index = InvertedIndex.load(arguments.path_to_load_index)
    for current_query in arguments.query:
        print(f'Get documents ids for query {current_query}...', file=sys.stderr)
        print(",".join([str(var) for var in inverted_index.query(current_query)]), file=sys.stdout)


def setup_parser(parser):
    """Setup cmd parser arguments

    :param parser: parser for arguments
    :return: nothing
    """
    subparsers = parser.add_subparsers(help="choose command")

    build_parser = subparsers.add_parser(
        "build",
        help="build inverted index from data and save it into hard drive",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    build_parser.add_argument(
        "-s", "--strategy", choices=['json', 'pickle'],
        dest="dump_strategy", default=DEFAULT_DUMP_STRATEGY,
        help="strategy to dump inverted index",
    )
    build_parser.add_argument(
        "-d", "--dataset", dest="path_to_load", required=True,
        help="path to dataset to load",
    )
    build_parser.add_argument(
        "-o", "--output", dest="path_to_store", required=True,
        help="path to store inverted index",
    )
    build_parser.set_defaults(callback=callback_build)

    query_parser = subparsers.add_parser(
        "query",
        help="query inverted index",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    query_parser.add_argument(
        "-i", "--json-index", dest="path_to_load_index", required=True,
        help="path to read inverted index",
    )
    query_parser.add_argument(
        "-q", "--query", required=True, nargs="+",
        action='append', metavar="word",
        help="query to run against inverted index",
    )
    query_parser.set_defaults(callback=callback_query)


def main():
    """Main function"""
    parser = ArgumentParser(
        prog='inverted-index',
        description="Inverted Index CLI",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()
