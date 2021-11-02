#!/usr/bin/env python3
"""
Module for Inverted Index library
"""
from __future__ import annotations
import sys
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType, ArgumentTypeError
from io import TextIOWrapper
import struct

import json
import re
from typing import Dict, List
from collections import defaultdict

DEFAULT_DUMP_STRATEGY = 'struct'


class EncodedFileType(FileType):
    """Class to fix encoding error with reading from buffer"""
    def __call__(self, string):
        if string == '-':
            if 'r' in self._mode:
                stdin = TextIOWrapper(sys.stdin.buffer, encoding=self._encoding)
                return stdin
            elif 'w' in self._mode:
                stdout = TextIOWrapper(sys.stdout.buffer, encoding=self._encoding)
                return stdout
            else:
                msg = 'argument "-" with mode %r' % self._mode
                raise ValueError(msg)
        try:
            return open(string, self._mode, self._bufsize, self._encoding, self._errors)
        except OSError as e:
            message = "can't open '%s': %s"
            raise ArgumentTypeError(message % (string, e))


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
        :param strategy: str - strategy to store: json or struct
        :return: nothing
        """
        strategy = strategy or DEFAULT_DUMP_STRATEGY
        if strategy == 'json':
            json_string = json.dumps(self.index_dict)
            with open(filepath, mode='w', encoding='utf8') as f_out:
                f_out.write(json_string)
        else:
            with open(filepath, 'wb') as f_out:
                for key, value in self.index_dict.items():
                    b_key = key.encode('utf8')
                    f_out.write(struct.pack(">H", len(b_key)))
                    f_out.write(b_key)
                    f_out.write(struct.pack(">H", len(value)))
                    f_out.write(struct.pack(">" + "H" * len(value), *value))

    @classmethod
    def load(cls, filepath: str, strategy='') -> InvertedIndex:
        """Upload InvertedIndex from file by filepath

        :param filepath: str - filepath to upload json_string
        :param strategy: str - strategy to store: json or struct
        :return: InvertedIndex - InvertedIndex object
        """
        strategy = strategy or DEFAULT_DUMP_STRATEGY
        print(f'Loading inverted index from {filepath} with strategy {strategy}', file=sys.stderr)
        loaded_string = {}
        if strategy == 'json':
            with open(filepath, mode='r', encoding='utf8') as fin:
                loaded_string = json.load(fin)
            inverted_index = InvertedIndex(loaded_string)
        else:
            with open(filepath, 'rb') as fin:
                file_size = os.fstat(fin.fileno()).st_size
                while file_size > 0:
                    b_len, = struct.unpack(">H", fin.read(2))
                    file_size -= 2
                    key = fin.read(b_len).decode("utf8")
                    file_size -= b_len
                    values_len, = struct.unpack(">H", fin.read(2))
                    file_size -= 2
                    values = list(struct.unpack(">" + "H" * values_len, fin.read(values_len * 2)))
                    file_size -= values_len * 2
                    loaded_string[key] = values
            inverted_index = InvertedIndex(loaded_string)
        return inverted_index

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
    :return: process_build
    """
    return process_build(arguments.path_to_load, arguments.path_to_store, arguments.dump_strategy)


def process_build(path_to_load, path_to_store, dump_strategy):
    """Process function for build

    :param path_to_load: path to load documents
    :param path_to_store: path to store inverted index
    :param dump_strategy: dump strategy
    :return: nothing
    """
    documents = load_documents(path_to_load)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(path_to_store, dump_strategy)


def callback_query(arguments):
    """Callback function for query

    :param arguments: cmd arguments
    :return: nothing
    """
    return process_queries(arguments.path_to_load_index, arguments.query_file,
                           arguments.query, arguments.load_strategy)


def process_queries(path_to_load_index, query_file, query, strategy):
    """Process function for query

    :param path_to_load_index: path to load index
    :param query_file: file with queries
    :param query: query without file
    :param strategy: inverted index load strategy
    :return: nothing
    """
    inverted_index = InvertedIndex.load(path_to_load_index, strategy)
    if query:
        for current_query in query:
            print(f'Get documents ids for query {current_query}...', file=sys.stderr)
            print(",".join([str(var) for var in inverted_index.query(current_query)]),
                  file=sys.stdout)
    else:
        for current_query in query_file:
            current_query = current_query.strip()
            print(f'Get documents ids for query {current_query}...', file=sys.stderr)
            print(",".join([str(var) for var in inverted_index.query(current_query.split())]),
                  file=sys.stdout)


def setup_parser(parser):
    """Setup cmd parser arguments

    :param parser: parser for arguments
    :return: nothing
    """
    subparsers = parser.add_subparsers(help="choose command")

    build_parser = subparsers.add_parser("build",
                                         help="build inverted index from data and save it to disc",
                                         formatter_class=ArgumentDefaultsHelpFormatter,)
    build_parser.add_argument("-s", "--strategy", choices=['json', 'struct'],
                              dest="dump_strategy",
                              default=DEFAULT_DUMP_STRATEGY,
                              help="strategy to dump inverted index",)
    build_parser.add_argument("-d", "--dataset", dest="path_to_load",
                              required=True, help="path to dataset to load",)
    build_parser.add_argument("-o", "--output", dest="path_to_store", required=True,
                              help="path to store inverted index",)
    build_parser.set_defaults(callback=callback_build)

    query_parser = subparsers.add_parser("query", help="query inverted index",
                                         formatter_class=ArgumentDefaultsHelpFormatter,)
    query_parser.add_argument("-i", "--index", dest="path_to_load_index",
                              required=True, help="path to read inverted index",)
    query_parser.add_argument("-s", "--strategy", choices=['json', 'struct'],
                              dest="load_strategy",
                              default=DEFAULT_DUMP_STRATEGY,
                              help="strategy to load inverted index", )
    query_file_group = query_parser.add_mutually_exclusive_group(required=True)
    query_file_group.add_argument("--query", nargs="+", action='append', metavar="word",
                                  dest="query", help="query to run against inverted index")
    query_file_group.add_argument("--query-file-utf8", dest="query_file",
                                  type=EncodedFileType('r', encoding="utf-8"),
                                  default=TextIOWrapper(sys.stdin.buffer, encoding="utf-8"),
                                  help="query file to get queries for inverted index",)
    query_file_group.add_argument("--query-file-cp1251", dest="query_file",
                                  type=EncodedFileType('r', encoding="cp1251"),
                                  default=TextIOWrapper(sys.stdin.buffer, encoding="cp1251"),
                                  help="query file to get queries for inverted index",)
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
