from textwrap import dedent

import pytest
import json
import os
from argparse import Namespace


from task_Smelova_Anna_inverted_index import (
    InvertedIndex, load_documents, callback_query,
    build_inverted_index, process_queries, callback_build
)

DICT_FOR_TEST = {'a': [1, 2], 'b': [2], 'c': [1, 3], 'd': [2, 3]}

DOCUMENTS_FOR_TEST = dedent("""\
    1\tFirst document info
    2\tSecond doc information doc
    3\tThird document information
    4\tFourth doc info
    5\tFifth docs information
    6\tSixs abc hjhjhj
    7\tSeventh 4 spaces
    8\tEights space user
    9\tNines phone information
    10\tTens docs number user
    11\tтекстовый запрос
    12\tзапрос
""")

EXPECTED_INDEX_STR_DICT = {
    1: 'first document info',
    2: 'second doc information doc',
    3: 'third document information',
    4: 'fourth doc info',
    5: 'fifth docs information',
    6: 'sixs abc hjhjhj',
    7: 'seventh 4 spaces',
    8: 'eights space user',
    9: 'nines phone information',
    10: 'tens docs number user',
    11: 'текстовый запрос',
    12: 'запрос'
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
    'number': [10],
    'текстовый': [11],
    'запрос': [11, 12]
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
    filename = 'inverted_index_dump.bin'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(filepath=temp_file_path)
    assert os.path.isfile(temp_file_path), (
        f'Dump was not created.'
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


def test_can_dump_inverted_index_to_file_struct_strategy(tmpdir):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    filename = 'inverted_index_dump.bin'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(filepath=temp_file_path, strategy='struct')
    assert os.path.isfile(temp_file_path), (
        f'Dump was not created.'
    )


def test_dump_inverted_index_with_empty_path():
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    with pytest.raises(FileNotFoundError):
        inverted_index.dump(filepath='')


def test_can_load_inverted_index_from_file_json_strategy(tmpdir, capsys):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    filename = 'inverted_index_dump.json'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(filepath=temp_file_path, strategy='json')
    loaded_inverted_index = InvertedIndex.load(filepath=temp_file_path, strategy='json')
    expected_inverted_index = inverted_index
    assert expected_inverted_index == loaded_inverted_index, (
        f'Bad loaded content.'
        f'File content is {loaded_inverted_index.index_dict}.'
        f'Expected content is {expected_inverted_index.index_dict}'
    )
    captured = capsys.readouterr()
    assert "Loading inverted index from" not in captured.out
    assert "Loading inverted index from" in captured.err


def test_can_load_inverted_index_from_file_struct_strategy(tmpdir, capsys):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    filename = 'inverted_index_dump.bin'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(filepath=temp_file_path, strategy='struct')
    loaded_inverted_index = InvertedIndex.load(filepath=temp_file_path, strategy='struct')
    expected_inverted_index = inverted_index
    assert expected_inverted_index == loaded_inverted_index, (
        f'Bad loaded content.'
        f'File content is {loaded_inverted_index.index_dict}.'
        f'Expected content is {expected_inverted_index.index_dict}'
    )
    captured = capsys.readouterr()
    assert "Loading inverted index from" not in captured.out
    assert "Loading inverted index from" in captured.err


def test_load_inverted_index_with_wrong_path(tmpdir):
    filename = 'inverted_index_dump.bin'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    with pytest.raises(FileNotFoundError):
        InvertedIndex.load(filepath=temp_file_path)


def test_load_inverted_index_with_empty_path():
    with pytest.raises(FileNotFoundError):
        InvertedIndex.load(filepath='')


def test_load_documents(documents_fio, capsys):
    documents = load_documents(filepath=documents_fio)
    assert documents == EXPECTED_INDEX_STR_DICT, (
        f'Wrong loaded documents'
        f'Loaded content is {documents}.'
        f'Expected content is {EXPECTED_INDEX_STR_DICT}'
    )
    captured = capsys.readouterr()
    assert "Loading documents from" not in captured.out
    assert "Loading documents from" in captured.err


def test_load_documents_wrong_path():
    with pytest.raises(FileNotFoundError):
        load_documents(filepath='wrong_path.txt')


def test_load_documents_empty_path():
    with pytest.raises(FileNotFoundError):
        load_documents(filepath='')


def test_build_inverted_index(documents_fio, capsys):
    documents = load_documents(filepath=documents_fio)
    inverted_index = build_inverted_index(documents)
    assert inverted_index.index_dict == EXPECTED_INDEX_DICT, (
        f'Wrong object construction.'
        f'Built index is {inverted_index.index_dict}.'
        f'Expected index is {EXPECTED_INDEX_DICT}'
    )
    captured = capsys.readouterr()
    assert "Building inverted index for provided" not in captured.out
    assert "Building inverted index for provided" in captured.err


def test_callback_build_struct_strategy(tmpdir):
    datapath = tmpdir.join('docs_for_test.txt')
    datapath.write(DOCUMENTS_FOR_TEST)
    tmp_fout = tmpdir.join('docs_for_test.dump')
    arguments = Namespace(
        path_to_load=datapath,
        path_to_store=tmp_fout,
        dump_strategy='struct'
    )
    callback_build(arguments)
    assert os.path.isfile(tmp_fout), 'Index was not created'


def test_callback_build_json_strategy(tmpdir):
    datapath = tmpdir.join('docs_for_test.txt')
    datapath.write(DOCUMENTS_FOR_TEST)
    tmp_fout = tmpdir.join('docs_for_test.dump')
    arguments = Namespace(
        path_to_load=datapath,
        path_to_store=tmp_fout,
        dump_strategy='json'
    )
    callback_build(arguments)
    assert os.path.isfile(tmp_fout), 'Index was not created'


def test_process_queries_can_process_all_queries_from_correct_file(tmpdir, capsys):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    filename = 'inverted_index_dump.json'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(filepath=temp_file_path, strategy='json')
    with open("queries.txt") as queries_fin:
        process_queries(path_to_load_index=temp_file_path, query_file=queries_fin, query='', strategy='json')
    captured = capsys.readouterr()
    assert "Get documents ids for query" not in captured.out
    assert "Get documents ids for query" in captured.err


def test_callback_query_can_process_all_queries_from_correct_file(tmpdir):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    filename = 'inverted_index_dump.json'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(filepath=temp_file_path, strategy='json')
    with open("queries.txt") as queries_fin:
        query_arguments = Namespace(
            path_to_load_index=temp_file_path,
            query_file=queries_fin,
            query='',
            load_strategy='json'
        )
        callback_query(query_arguments)


@pytest.mark.parametrize(
    "query, expected_answer",
    [
        pytest.param([['a', 'c']], [1], id='two different values'),
        pytest.param([[]], [], id='empty query'),
        pytest.param([['f']], [], id='value not in dict'),
        pytest.param([['d']], [2, 3], id='one value from dict'),
    ]
)
def test_callback_query_can_process_query(tmpdir, capsys, query, expected_answer):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    filename = 'inverted_index_dump.json'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(filepath=temp_file_path, strategy='json')
    arguments = Namespace(
        path_to_load_index=temp_file_path,
        query_file='',
        query=query,
        load_strategy='json'
    )
    callback_query(arguments)
    captured = capsys.readouterr()
    print(f'captured.out={captured.out}')
    if captured.out == "\n":
        query_answer = []
    else:
        query_answer = [int(var) for var in captured.out.rstrip().split(",")]
    assert query_answer == expected_answer, (
        f'Wrong answer for query {query}.',
        f'Query answer is {query_answer}.'
        f'Expected answer is {expected_answer}'
    )


@pytest.mark.parametrize(
    "query, expected_answer",
    [
        pytest.param(['a', 'c'], [1], id='two different values'),
        pytest.param([], [], id='empty query'),
        pytest.param(['f'], [], id='value not in dict'),
        pytest.param(['d'], [2, 3], id='one value from dict'),
    ]
)
def test_callback_query_utf8(tmpdir, capsys, query, expected_answer):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    filename = 'inverted_index.dump'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(temp_file_path)
    tmp_file = tmpdir.join('test_queries.utf8')
    with open(tmp_file, "w", encoding="utf8") as file:
        file.write(" ".join(query) + "\n")
    arguments = Namespace(
        path_to_load_index=temp_file_path,
        query_file=open(tmp_file, "r", encoding="utf8"),
        query='',
        load_strategy=''
    )
    callback_query(arguments)
    captured = capsys.readouterr()
    if captured.out == "\n":
        query_answer = []
    else:
        query_answer = [int(var) for var in captured.out.rstrip().split(",")]
    assert query_answer == expected_answer, (
        f'Wrong answer for query {query}.',
        f'Query answer is {query_answer}.'
        f'Expected answer is {expected_answer}'
    )


@pytest.mark.parametrize(
    "query, expected_answer",
    [
        pytest.param(['a', 'c'], [1], id='two different values'),
        pytest.param([], [], id='empty query'),
        pytest.param(['f'], [], id='value not in dict'),
        pytest.param(['d'], [2, 3], id='one value from dict'),
    ]
)
def test_callback_query_cp1251(tmpdir, capsys, query, expected_answer):
    inverted_index = InvertedIndex(index_dict=DICT_FOR_TEST)
    filename = 'inverted_index.dump'
    temp_file = tmpdir.join(filename)
    temp_file_path = str(temp_file)
    inverted_index.dump(temp_file_path)
    tmp_file = tmpdir.join('test_queries.cp1251')
    with open(tmp_file, "w", encoding="cp1251") as file:
        file.write(" ".join(query) + "\n")
    arguments = Namespace(
        path_to_load_index=temp_file_path,
        query_file=open(tmp_file, "r", encoding="cp1251"),
        query='',
        load_strategy=''
    )
    callback_query(arguments)
    captured = capsys.readouterr()
    if captured.out == "\n":
        query_answer = []
    else:
        query_answer = [int(var) for var in captured.out.rstrip().split(",")]
    assert query_answer == expected_answer, (
        f'Wrong answer for query {query}.',
        f'Query answer is {query_answer}.'
        f'Expected answer is {expected_answer}'
    )


def test_entrypoint():
    exit_status = os.system('python3 task_Smelova_Anna_inverted_index.py -h')
    assert exit_status == 0
