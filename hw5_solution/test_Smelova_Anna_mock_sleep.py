from argparse import Namespace
from unittest.mock import call, patch
import pytest

from sleepy import sleep_add, sleep_multiply

ADD_SLEEP_TIME = 3
MULTIPLY_SLEEP_TIME = 5


@patch("sleepy.sleep")
def test_sleep_add_function(mock_sleepy_sleep):
    add_result = sleep_add(-1, 1)
    assert 0 == add_result, (
        'Wrong result of add function'
        f'Result is {add_result}'
        f'Expected revenue is {0}'
    )
    mock_sleepy_sleep.assert_called_once_with(ADD_SLEEP_TIME)


@patch("time.sleep")
def test_sleep_multiply_function(mock_time_sleep):
    prod_result = sleep_multiply(-1, -1)
    assert 1 == prod_result, (
        'Wrong result of multiply function'
        f'Result is {prod_result}'
        f'Expected revenue is {1}'
    )
    mock_time_sleep.assert_called_once_with(MULTIPLY_SLEEP_TIME)
