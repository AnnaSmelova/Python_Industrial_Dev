from textwrap import dedent

import pytest
import json

from task_Smelova_Anna_inverted_index_cli import InvertedIndex, load_documents, build_inverted_index

DICT_FOR_TEST = {'a': [1, 2], 'b': [2], 'c': [1, 3], 'd': [2, 3]}

DOCUMENTS_FOR_TEST = dedent("""\
    1\tFirst document info
    2\tSecond doc information
    3\tThird document information
    4\tFourth doc info
    5\tFifth docs information
    6\tSixs abc hjhjhj
    7\tSeventh 4 spaces
    8\tEights space user
    9\tNines phone information
    10\tTens docs number user
""")

EXPECTED_INDEX_STR_DICT = {
    1: 'first document info',
    2: 'second doc information',
    3: 'third document information',
    4: 'fourth doc info',
    5: 'fifth docs information',
    6: 'sixs abc hjhjhj',
    7: 'seventh 4 spaces',
    8: 'eights space user',
    9: 'nines phone information',
    10: 'tens docs number user'
}

EXPECTED_INDEX_DICT = {
    'first': [1],
    'document': [1, 3],
    'info': [1, 4],
    'second': [2],
    'doc': [2, 4],
    'information': [2, 3, 5, 9],
    'third': [3],
    'fourth': [4],
    'fifth': [5],
    'docs': [5, 10],
    'sixs': [6],
    'abc': [6],
    'hjhjhj': [6],
    'seventh': [7],
    '4': [7],
    'spaces': [7],
    'eights': [8],
    'space': [8],
    'user': [8, 10],
    'nines': [9],
    'phone': [9],
    'tens': [10],
    'number': [10]
}


@pytest.fixture()
def documents_fio(tmpdir):
    dataset_fio = tmpdir.join("docs_test.txt")
    dataset_fio.write(DOCUMENTS_FOR_TEST)
    return dataset_fio


def test_can_initialize_inverted_index():
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)


@pytest.mark.parametrize(
    "query, expected_answer",
    [
        pytest.param(['a', 'c'], [1], id='two different values'),
        pytest.param([], [], id='empty query'),
        pytest.param(['f'], [], id='value not in dict'),
        pytest.param(['d'], [2, 3], id='one value from dict'),
    ]
)
def test_return_of_query_method(query, expected_answer):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    real_result = inverted_index.query(words=query)
    assert sorted(expected_answer) == sorted(real_result), (
        f'All of words should be present in documents.'
        f'Your result is {real_result}.'
        f'Expected result is {expected_answer}'
    )


def test_query_method_for_bad_query():
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    query = 1
    with pytest.raises(TypeError):
        inverted_index.query(words=query)


def test_can_dump_inverted_index_to_file_default_strategy(tmpdir):
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


def test_can_dump_inverted_index_to_file_json_strategy(tmpdir):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    expected_json_string = json.dumps(inverted_index.index_dict)
    filename = 'inverted_index_dump.json'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(filepath=temp_file_path, strategy='json')
    result = temp_file.read()
    assert result == expected_json_string, (
        f'Bad file content.'
        f'File content is {result}.'
        f'Expected content is {expected_json_string}'
    )


def test_can_dump_inverted_index_to_file_pickle_strategy(tmpdir):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    expected_json_string = json.dumps(inverted_index.index_dict)
    filename = 'inverted_index_dump.json'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(filepath=temp_file_path, strategy='pickle')


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


def test_load_documents(documents_fio):
    documents = load_documents(filepath=documents_fio)
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


def test_build_inverted_index(documents_fio):
    documents = load_documents(filepath=documents_fio)
    inverted_index = build_inverted_index(documents)
    assert inverted_index.index_dict == EXPECTED_INDEX_DICT, (
        f'Wrong object construction.'
        f'Builded index is {inverted_index.index_dict}.'
        f'Expected index is {EXPECTED_INDEX_DICT}'
    )
