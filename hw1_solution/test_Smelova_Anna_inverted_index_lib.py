import pytest
import json

from task_Smelova_Anna_inverted_index_lib import InvertedIndex, load_documents, build_inverted_index

DICT_FOR_TEST = {'a': [1, 2], 'b': [2], 'c': [1, 3], 'd': [2, 3]}

DOCUMENTS_FOR_TEST = """\
    1\tFirst document info
    2\tSecond doc information
    3\tThird document information
    4\tFourth doc info
    5\tFifth docs information
"""

EXPECTED_INDEX_STR_DICT = {
    1: 'first document info',
    2: 'second doc information',
    3: 'third document information',
    4: 'fourth doc info',
    5: 'fifth docs information'
}

EXPECTED_INDEX_DICT = {
    'first': [1],
    'document': [1, 3],
    'info': [1, 4],
    'second': [2],
    'doc': [2, 4],
    'information': [2, 3, 5],
    'third': [3],
    'fourth': [4],
    'fifth': [5],
    'docs': [5]
}


def test_can_initialize_inverted_index():
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)


def test_return_of_query_method():
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    query = ['a', 'c']
    expected_result = [1]
    real_result = inverted_index.query(words=query)
    assert expected_result == real_result, (
        f'All of words should be present in documents.'
        f'Your result is {real_result}.'
        f'Expected result is {expected_result}'
    )


def test_return_query_method_for_empty_query():
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    query = []
    expected_result = []
    real_result = inverted_index.query(words=query)
    assert expected_result == real_result, (
        f'Empty list should be for empty query.'
        f'Your result is {real_result}.'
        f'Expected result is {expected_result}'
    )


def test_return_query_method_for_words_not_from_dict():
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    query = ['f']
    expected_result = []
    real_result = inverted_index.query(words=query)
    assert expected_result == real_result, (
        f'Empty list should be for words not from dict.'
        f'Your result is {real_result}.'
        f'Expected result is {expected_result}'
    )


def test_query_method_for_bad_query():
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    query = 1
    with pytest.raises(TypeError):
        inverted_index.query(words=query)


def test_can_dump_inverted_index_to_file(tmpdir):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    expected_json_string = json.dumps(inverted_index.index_dict)
    filename = 'inverted_index_dump.json'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(filepath=temp_file_path)
    result = temp_file.read()
    assert result == expected_json_string, (
        f'Bad file content.'
        f'File content is {result}.'
        f'Expected content is {expected_json_string}'
    )


def test_dump_inverted_index_with_empty_path():
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    with pytest.raises(FileNotFoundError):
        inverted_index.dump(filepath='')


def test_can_load_inverted_index_from_file(tmpdir):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    filename = 'inverted_index_dump.json'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(filepath=temp_file_path)
    loaded_inverted_index = InvertedIndex.load(filepath=temp_file_path)
    expected_inverted_index = inverted_index
    assert expected_inverted_index == loaded_inverted_index, (
        f'Bad loaded content.'
        f'File content is {loaded_inverted_index.index_dict}.'
        f'Expected content is {expected_inverted_index.index_dict}'
    )


def test_load_inverted_index_with_wrong_path(tmpdir):
    filename = 'inverted_index_dump.json'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    with pytest.raises(FileNotFoundError):
        InvertedIndex.load(filepath=temp_file_path)


def test_load_inverted_index_with_empty_path():
    with pytest.raises(FileNotFoundError):
        InvertedIndex.load(filepath='')


def test_load_documents(tmpdir):
    datapath = tmpdir.join('test_documents.txt')
    datapath.write(DOCUMENTS_FOR_TEST)
    documents = load_documents(filepath=datapath)
    assert documents == EXPECTED_INDEX_STR_DICT, (
        f'Wrong loaded documents'
        f'Loaded content is {documents}.'
        f'Expected content is {EXPECTED_INDEX_STR_DICT}'
    )


def test_load_documents_wrong_path():
    with pytest.raises(FileNotFoundError):
        load_documents(filepath='wrong_path.txt')


def test_load_documents_empty_path():
    with pytest.raises(FileNotFoundError):
        load_documents(filepath='')


def test_build_inverted_index(tmpdir):
    datapath = tmpdir.join('test_documents.txt')
    datapath.write(DOCUMENTS_FOR_TEST)
    documents = load_documents(filepath=datapath)
    inverted_index = build_inverted_index(documents)
    assert inverted_index.index_dict == EXPECTED_INDEX_DICT, (
        f'Wrong object construction.'
        f'Builded index is {inverted_index.index_dict}.'
        f'Expected index is {EXPECTED_INDEX_DICT}'
    )
