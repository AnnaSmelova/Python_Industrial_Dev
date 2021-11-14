import logging
from textwrap import dedent

import pytest
import os

from asset import Asset, load_asset_from_file, print_asset_revenue


TEST_ASSET_TXT = dedent("""\
property   1000    0.1
""")
TEST_RAW = 'property   1000    0.1'


@pytest.fixture()
def test_asset_txt(tmpdir):
    fio = tmpdir.join("test_asset.txt")
    fio.write(TEST_ASSET_TXT)
    return fio


def test_can_initialize_asset():
    asset = Asset('property', 1000, 0.1)
    assert 'property' == asset.name and 1000 == asset.capital \
           and 0.1 == asset.interest, 'Can not initialize asset'


@pytest.mark.parametrize(
    "years, expected_revenue",
    [
        pytest.param(1, 1000 * (1.1 ** 1 - 1.0)),
        pytest.param(5, 1000 * (1.1 ** 5 - 1.0)),
        pytest.param(10, 1000 * (1.1 ** 10 - 1.0))
    ]
)
def test_return_of_calculate_revenue(years, expected_revenue):
    asset = Asset('property', 1000, 0.1)
    revenue = asset.calculate_revenue(years)
    assert expected_revenue == revenue, (
        f'Wrong revenue'
        f'Result is {round(revenue, 4)}'
        f'Expected revenue is {round(expected_revenue, 4)}'
    )


def test_repr():
    asset = Asset('property', 1000, 0.1)
    assert 'Asset(property, 1000, 0.1)' == repr(asset), (
        f'Wrong repr'
        f'Result is {repr(asset)}' 
        f'Expected Asset(property, 1000, 0.1)'
    )


def test_can_build_from_str(caplog):
    with caplog.at_level('DEBUG'):
        asset = Asset.build_from_str(raw=TEST_RAW)
        assert 'Asset(property, 1000.0, 0.1)' == repr(asset), (
            f'Wrong repr'
            f'Result is {repr(asset)}'
            f'Expected Asset(property, 1000.0, 0.1)'
        )
        assert any('building asset object...' in message for message in caplog.messages), (
            'There is no DEBUG building message in logs'
        )


def test_can_load_asset_from_file(test_asset_txt, caplog):
    with caplog.at_level('INFO'):
        asset = load_asset_from_file(fileio=test_asset_txt)
        assert 'Asset(property, 1000.0, 0.1)' == repr(asset), (
            f'Bad loaded asset.'
            f'Loaded asset is {repr(asset)}.'
            f'Expected asset is Asset(property, 1000.0, 0.1)'
        )
        assert any('reading asset file...' in message for message in caplog.messages), (
            'There is no INFO reading file message in logs'
        )


def test_warning_about_big_len_periods(test_asset_txt, caplog):
    with caplog.at_level('WARNING'):
        print_asset_revenue(test_asset_txt, [1, 5, 10, 15, 20, 25])

        assert any('too many periods were provided: 6' in message for message in caplog.messages), (
            'There is no WARN_PERIOD_THRESHOLD message in logs'
        )


def test_print_asset_revenue(test_asset_txt, capsys, caplog):
    with caplog.at_level('DEBUG'):
        print_asset_revenue(test_asset_txt, [1, 5, 10])
        captured = capsys.readouterr()
        assert '    1:    100.000' in captured.out

        assert any('asset Asset(property, 1000.0, 0.1) for period 1 gives 100.00000000000009' \
                   in message for message in caplog.messages), (
            'There is no DEBUG "asset" message in logs'
        )

        assert all(record.levelno <= logging.WARNING for record in caplog.records), (
            'Application is unstable, there are WARNING+ messages in logs'
        )


def test_entrypoint():
    exit_status = os.system('python3 asset.py -h')
    assert exit_status == 0
