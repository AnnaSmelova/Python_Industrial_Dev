from __future__ import annotations

import json
import re
from typing import Dict, List


class InvertedIndex:
    def __init__(self, index_dict: Dict[str, List[int]]) -> None:
        """
        Class constructor
        Parameters
        ----------
        index_dict: Dict[str, List[int]]
            dictionary with terms as keys and lists of docs ids as values
        Returns
        ----------
        Nothing
        """
        self.index_dict = index_dict

    def query(self, words: List[str]) -> List[int]:
        """
        Return the list of relevant documents for the given query
        Parameters
        ----------
        words: List[str]
            list of words
        Returns
        ----------
        result_of_query: List[int]
            list of docs ids which include ALL words from query
        """
        result_of_query = []
        if words:
            current_set = set()
            for word in words:
                if word in self.index_dict.keys():
                    if not current_set:
                        current_set = set(self.index_dict[word])
                    else:
                        current_set.intersection_update(set(self.index_dict[word]))
            result_of_query = list(current_set)
        return result_of_query

    def dump(self, filepath: str) -> None:
        """
        Convert index_dict into string and stores it in json_string
        And write it to filepath
        Parameters
        ----------
        filepath: str
            filepath to write json_string
        Returns
        ----------
        Nothing
        """
        json_string = json.dumps(self.index_dict)
        with open(filepath, mode='w', encoding='utf8') as fout:
            fout.write(json_string)

    @classmethod
    def load(cls, filepath: str) -> InvertedIndex:
        """
        Upload InvertedIndex from file by filepath
        Parameters
        ----------
        filepath: str
            filepath to upload json_string
        Returns
        ----------
        inverted_index: InvertedIndex
            InvertedIndex object
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


def load_documents(filepath: str) -> Dict[int, str]:
    """
    Upload Documents from file by filepath
    Parameters
    ----------
    filepath: str
        filepath to upload docs
    Returns
    ----------
    documents_dict: Dict[int, str]
        Dictionary of documents in format id: str
    """
    documents_dict = {}
    with open(filepath, mode='r', encoding='utf8') as fin:
        for line in fin:
            doc_id, content = line.lower().strip().split("\t", 1)
            doc_id = int(doc_id)
            documents_dict[doc_id] = content
    return documents_dict


def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """
    Build inverted index from documents_dict
    Parameters
    ----------
    documents: Dict[int, str]
        Dictionary of documents in format id: str
    Returns
    ----------
    inverted_index: InvertedIndex
        InvertedIndex object
    """
    index_dict = {}
    for doc_id, content in documents.items():
        words = re.split(r"\W+", content)
        for word in words:
            dict_keys = index_dict.keys()
            if word in dict_keys:
                if doc_id not in index_dict[word]:
                    index_dict[word].append(doc_id)
            else:
                index_dict[word] = [doc_id]
    return InvertedIndex(index_dict=index_dict)


def main():
    documents = load_documents('wikipedia_sample')
    inverted_index = build_inverted_index(documents)
    inverted_index.dump('inverted_index')
    inverted_index = InvertedIndex.load('inverted_index')
    document_ids = inverted_index.query(["two", "words"])


if __name__ == "__main__":
    main()
