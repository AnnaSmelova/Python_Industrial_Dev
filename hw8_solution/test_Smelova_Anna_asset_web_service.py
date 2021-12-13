import pytest
from unittest.mock import patch
from collections import namedtuple
from task_Smelova_Anna_asset_web_service import \
    Asset, Storage, DAILY_URL, KEY_INDICATORS_URL, app, \
    custom_float, parse_cbr_currency_base_daily, parse_cbr_key_indicators


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_can_initialize_asset():
    asset = Asset('Anya', 10.0, 1.5, 'USD')
    assert 'Anya' == asset.name and 10.0 == asset.capital and 1.5 == asset.interest, (
        f'Wrong asset initialization'
    )


@pytest.mark.parametrize(
    'years, expected_result',
    [
        pytest.param(1, 10 * (2.5 ** 1 - 1.0)),
        pytest.param(5, 10 * (2.5 ** 5 - 1.0)),
        pytest.param(10, 10 * (2.5 ** 10 - 1.0))
    ]
)
def test_calc_revenue(years, expected_result):
    asset = Asset('Anya', 10.0, 1.5, 'USD')
    calculated_revenue = asset.calculate_revenue(years)
    assert expected_result == calculated_revenue, (
        f'Wrong revenue: expected {expected_result}, '
        f"get {calculated_revenue}"
    )


def test_asset_repr():
    new_asset = Asset('Anya', 10.0, 1.5, 'USD')
    assert repr(new_asset) == 'Asset(Anya, 10.0, 1.5, USD)', (
        f'Wrong repr: {repr(new_asset)}, '
        f'expected: Asset(Vasya, 12.0, 0.5)')


def test_asset_error():
    left = Asset('Anya', 10.0, 1.5, 'USD')
    with pytest.raises(ValueError):
        left < '11111'


@pytest.mark.parametrize(
    'left_value, right_value, expected_result',
    [
        pytest.param(Asset('Alice', 10, 5, 'USD'), Asset('Diana', 50, 1, 'EUR'), True),
        pytest.param(Asset('Diana', 10, 1, 'RUB'), Asset('Alice', 100, 5, 'USD'), False),
        pytest.param(Asset('Alice', 10, 5, 'RUB'), Asset('Diana', 50, 1, 'USD'), True)
    ]
)
def test_asset_lt(left_value, right_value, expected_result):
    assert (left_value < right_value) is expected_result, (
        f'Wrong lt comparison: left {left_value.name}, right {right_value.name} ' 
        f'expected_result {left_value < right_value}'
    )


@pytest.mark.parametrize(
    'data, expected_result',
    [
        pytest.param([Asset('Anya', 10, 1, 'USD'),
                      Asset('Alice', 15, 2, 'USD'),
                      Asset('Diana', 5, 0, 'USD')],
                     sorted(['Anya', 'Alice', 'Diana'])),
        pytest.param(None, [])
    ]
)
def test_can_initialize_storage(data, expected_result):
    storage = Storage(data)
    names = [var.name for var in storage.asset_list]
    assert expected_result == names, (
        f'Wrong initialization: {names}, '
        f'expected: {expected_result}'
    )


def test_storage_add_asset_char_code():
    asset_1 = Asset('Anya', 10, 1, 'RUB')
    asset_2 = Asset('Alice', 15, 2, 'EUR')
    asset_3 = Asset('Diana', 5, 0, 'USD')
    expected_result = sorted(['USD', 'EUR', 'RUB'])
    bank = Storage([asset_1, asset_3])
    bank.add_asset(asset_2)
    char_codes = [var.char_code for var in bank.asset_list]
    assert expected_result == char_codes, (
        f'Wrong result: {char_codes}, '
        f'expected: {expected_result}'
    )


def test_storage_add_asset_name():
    asset_1 = Asset('Anya', 10, 1, 'USD')
    asset_2 = Asset('Alice', 15, 2, 'USD')
    asset_3 = Asset('Diana', 5, 0, 'USD')
    expected_result = sorted(['Anya', 'Alice', 'Diana'])
    bank = Storage([asset_1, asset_3])
    bank.add_asset(asset_2)
    names = [var.name for var in bank.asset_list]
    assert expected_result == names, (
        f'Wrong result: {names}, '
        f'expected: {expected_result}'
    )


@pytest.mark.parametrize(
    'asset, expected_result',
    [
        pytest.param(Asset('Anya', 10, 1, 'USD'), True),
        pytest.param(Asset('Alice', 15, 2, 'USD'), False)
    ]
)
def test_storage_is_contains(asset, expected_result):
    asset_1 = Asset('Anya', 10, 1, 'USD')
    asset_2 = Asset('Diana', 15, 2, 'USD')
    bank = Storage([asset_1, asset_2])
    result = bank.is_contains(asset)
    assert expected_result == result, (
        f'Wrong result: {result}, '
        f'expected: {expected_result}'
    )


def test_storage_get_json():
    asset_1 = Asset('Anya', 10, 1, 'USD')
    asset_2 = Asset('Diana', 15, 2, 'RUB')
    expected_result = [
        ['RUB', 'Diana', 15, 2],
        ['USD', 'Anya', 10, 1]
    ]
    bank = Storage([asset_1, asset_2])
    result = bank.get_json()
    assert expected_result == result, (
        f'Wrong result: {result}, '
        f'expected: {expected_result}'
    )


def test_storage_clear_storage():
    asset_1 = Asset('Anya', 10, 1, 'USD')
    asset_2 = Asset('Diana', 15, 2, 'RUB')
    bank = Storage([asset_1, asset_2])
    bank.clear_storage()
    assert 0 == len(bank.asset_list), (
        f'Wrong result: {len(bank.asset_list)}, '
        f'expected: 0'
    )


def test_storage_get_assets():
    asset_1 = Asset('Anya', 10, 1, 'USD')
    asset_2 = Asset('Diana', 15, 2, 'RUB')
    bank = Storage([asset_1, asset_2])
    result = bank.get_assets('Anya')
    expected_result = ['USD', 'Anya', 10, 1]
    assert expected_result == result, (
        f'Wrong result: {result}, '
        f'expected: {expected_result}'
    )


def test_storage_get_assets_not_existed():
    asset_1 = Asset('Anya', 10, 1, 'USD')
    asset_2 = Asset('Diana', 15, 2, 'RUB')
    bank = Storage([asset_1, asset_2])
    result = bank.get_assets('Alice')
    expected_result = []
    assert expected_result == result, (
        f'Wrong result: {result}, '
        f'expected: {expected_result}'
    )


def test_storage_get_total_revenue():
    asset_1 = Asset('Anya', 10, 1, 'USD')
    asset_2 = Asset('Alice', 15, 2, 'EUR')
    asset_3 = Asset('Diana', 5, 0, 'JPY')
    asset_4 = Asset('Veronika', 50, 10, 'GBP')
    key_indicator_map = {
        'USD': 73.6,
        'EUR': 83.1,
    }
    daily_map = {
        'JPY': 64.8,
        'GBP': 97.2
    }
    years = 5
    expected_result = asset_1.calculate_revenue(years) * 73.6
    expected_result += asset_2.calculate_revenue(years) * 83.1
    expected_result += asset_3.calculate_revenue(years) * 64.8
    expected_result += asset_4.calculate_revenue(years) * 97.2
    bank = Storage([asset_1, asset_2, asset_3, asset_4])
    result = bank.get_total_revenue(years, key_indicator_map, daily_map)
    assert expected_result == result, (
        f'Wrong result: {result}, '
        f'expected: {expected_result}'
    )


def test_storage_custom_float():
    expected_result = 1234.56
    result = custom_float('1,234.56')
    assert expected_result == result, (
        f'Wrong result: {result}, '
        f'expected: {expected_result}'
    )


def test_parse_cbr_currency_base_daily():
    expected_result = {
        'AUD': 57.0229,
        'AZN': 44.4127,
        'AMD': 0.144485
    }
    with open('cbr_currency_base_daily.html', 'r', encoding='utf8') as f:
        result = parse_cbr_currency_base_daily(f.read())
    assert expected_result['AUD'] == result['AUD'] and \
           expected_result['AZN'] == result['AZN'] and \
           expected_result['AMD'] == result['AMD'], (
        f'Wrong result: {result}, '
        f'expected: {expected_result}'
    )


def test_parse_cbr_key_indicators():
    expected_result = {
        'USD': 75.4571,
        'EUR': 91.9822,
        'Au': 4529.59,
        'Ag': 62.52,
        'Pt': 2459.96,
        'Pd': 5667.14
    }
    with open('cbr_key_indicators.html', 'r', encoding='utf8') as f:
        result = parse_cbr_key_indicators(f.read())
    assert expected_result == result, (
        f'Wrong result: {result}, '
        f'expected: {expected_result}'
    )


@patch('requests.get')
def test_cbr_daily_api(mock_get, client):
    with open('cbr_currency_base_daily.html', 'r', encoding='utf8') as f:
        mock_get.return_value.text = f.read()
    mock_get.return_value.status_code = 200
    expected_result = {
        'AUD': 57.0229,
        'AZN': 44.4127,
        'AMD': 0.144485,
    }
    result = client.get('/cbr/daily')
    mock_get.called_once(DAILY_URL)
    result = result.json
    assert expected_result['AUD'] == result['AUD'] and \
           expected_result['AZN'] == result['AZN'] and \
           expected_result['AMD'] == result['AMD'], (
        f'Wrong result: {result}, '
        f'expected: {expected_result}'
    )


@patch('requests.get')
def test_cbr_key_indicator_api(mock_get, client):
    with open('cbr_key_indicators.html', 'r', encoding='utf8') as f:
        mock_get.return_value.text = f.read()
    mock_get.return_value.status_code = 200
    expected_result = {
        'USD': 75.4571,
        'EUR': 91.9822,
        'Au': 4529.59,
        'Ag': 62.52,
        'Pt': 2459.96,
        'Pd': 5667.14
    }
    result = client.get("/cbr/key_indicators")
    mock_get.called_once(KEY_INDICATORS_URL)
    assert expected_result == result.json, (
        f'Wrong result: {result.json}, '
        f'expected: {expected_result}'
    )


def test_bad_route_api(client):
    expected_result = 'This route is not found'
    result = client.get('/cbr/weekly')
    assert 404 == result.status_code, (
        f'Wrong status_code: {result.status_code}, '
        f'expected: 404'
    )
    assert expected_result == result.data.decode(), (
        f'Wrong message: {result.data.decode()}, '
        f'expected: {expected_result}'
    )


@patch('requests.get')
def test_cbr_daily_api_unavailable(mock_get, client):
    mock_get.return_value.status_code = 503
    expected_result = 'CBR service is unavailable'
    result = client.get('/cbr/daily')
    mock_get.called_once(DAILY_URL)
    assert 503 == result.status_code, (
        f'Wrong status_code: {result.status_code}, '
        f'expected: 503'
    )
    assert expected_result == result.data.decode(), (
        f'Wrong message: {result.data.decode()}, '
        f'expected: {expected_result}'
    )


@patch('requests.get')
def test_cbr_key_indicator_api_unavailable(mock_get, client):
    mock_get.return_value.status_code = 503
    expected_result = 'CBR service is unavailable'
    result = client.get('/cbr/key_indicators')
    mock_get.called_once(KEY_INDICATORS_URL)
    assert 503 == result.status_code, (
        f'Wrong status_code: {result.status_code}, '
        f'expected: 503'
    )
    assert expected_result == result.data.decode(), (
        f'Wrong message: {result.data.decode()}, '
        f'expected: {expected_result}'
    )


@pytest.mark.parametrize(
    'route, expected_result, lng',
    [
        pytest.param('/api/asset/add/EUR/Diana/10/1.0', ('EUR', 'Diana', 10, 1), 1),
        pytest.param('/api/asset/add/USD/Anya/15/2.0', ('USD', 'Anya', 15, 2), 2)
    ]
)
def test_add_asset_api(route, expected_result, lng, client):
    response = client.get(route)
    asset = (
        client.application.bank.asset_list[0].char_code,
        client.application.bank.asset_list[0].name,
        client.application.bank.asset_list[0].capital,
        client.application.bank.asset_list[0].interest
    )
    banks_cnt = len(client.application.bank.asset_list)
    message = f"Asset '{asset[1]}' was successfully added"
    assert 200 == response.status_code, (
        f'Wrong status code: {response.status_code}, '
        f'expected: 200'
    )
    assert message == response.data.decode(), (
        f'Wrong message: {response.data.decode()}, '
        f'expected {message}'
    )
    assert expected_result == asset, (
        f'Wrong result: {asset}, '
        f'expected: {expected_result}'
    )
    assert lng == banks_cnt, (
        f'Wrong bank count: {banks_cnt}, '
        f'expected: {lng}'
    )


@pytest.mark.parametrize(
    'route, expected_message, expected_status_code',
    [
        pytest.param('/api/asset/add/EUR/Diana/100/5.0', "Name has already exist", 403)
    ]
)
def test_add_existed_asset_api(route, expected_message, expected_status_code, client):
    response = client.get(route)
    assert expected_status_code == response.status_code, (
        f'Wrong status code: {response.status_code}, '
        f'expected: 200'
    )
    assert expected_message == response.data.decode(), (
        f'Wrong message: {response.data.decode()}, '
        f'expected {expected_message}'
    )


def test_asset_list_api(client):
    client.application.bank = Storage([
        Asset('Anya', 10, 1, 'USD'),
        Asset('Alice', 15, 2, 'EUR'),
        Asset('Diana', 5, 0, 'RUB')
    ])
    expected_result = [
        ['EUR', 'Alice', 15, 2],
        ['RUB', 'Diana', 5, 0],
        ['USD', 'Anya', 10, 1]
    ]
    result = client.get('/api/asset/list')
    assert expected_result == result.json, (
        f'Wrong result: {result.json}, '
        f'expected: {expected_result}'
    )
    assert 200 == result.status_code, (
        f'Wrong status code: {result.status_code}, '
        f'expected 200'
    )


@pytest.mark.parametrize(
    "route, expected_result",
    [
        pytest.param("/api/asset/get?name=Anya&name=Alice",
                     [
                         ['EUR', 'Alice', 15, 2],
                         ['USD', 'Anya', 10, 1]
                     ]
                     ),
        pytest.param("/api/asset/get?name=Diana",
                     [
                         ['RUB', 'Diana', 5, 0],
                     ]
                     ),
        pytest.param("/api/asset/get?name=Vitaly",
                     []
                     ),
    ]
)
def test_asset_get_api(route, expected_result, client):
    client.application.bank = Storage([
        Asset('Diana', 5, 0, 'RUB'),
        Asset('Anya', 10, 1, 'USD'),
        Asset('Alice', 15, 2, 'EUR'),
        Asset('Veronika', 50, 10, 'GBP'),
    ])
    result = client.get(route)
    assert expected_result == result.json,  (
        f'Wrong result: {result.json}, '
        f'expected: {expected_result}'
    )
    assert 200 == result.status_code, (
        f'Wrong status code: {result.status_code}, '
        f'expected 200'
    )


@patch('requests.get')
@pytest.mark.parametrize(
    'route, periods',
    [
        pytest.param('/api/asset/calculate_revenue?period=3', [3]),
        pytest.param('/api/asset/calculate_revenue?period=3&period=5', [3, 5])
    ]
)
def test_asset_calc_revenue_api(mock_get, route, periods, client):
    side_effect = []
    return_value = namedtuple('return_value', ['text', 'status_code'])
    with open('cbr_key_indicators.html', 'r', encoding='utf8') as f:
        side_effect.append(return_value(f.read(), 200))
    with open('cbr_currency_base_daily.html', 'r', encoding='utf8') as f:
        side_effect.append(return_value(f.read(), 200))
    mock_get.side_effect = side_effect
    daily = {
        'AUD': 57.0229,
        'AZN': 44.4127,
        'AMD': 0.144485
    }
    interest = {
        'USD': 75.4571,
        'EUR': 91.9822,
        'Au': 4529.59,
        'Ag': 62.52,
        'Pt': 2459.96,
        'Pd': 5667.14
    }
    client.application.bank = Storage([
        Asset('Diana', 5, 0, 'AMD'),
        Asset('Anya', 10, 1, 'EUR'),
        Asset('Alice', 15, 2, 'Au'),
        Asset('Veronika', 50, 10, 'AUD'),
    ])
    expected_result = dict()
    for period in periods:
        expected_result[str(period)] = client.application.bank.get_total_revenue(period, interest, daily)
    result = client.get(route)
    mock_get.called_once(KEY_INDICATORS_URL)
    mock_get.called_once(DAILY_URL)
    expected_result = dict(expected_result)
    assert expected_result == result.json, (
        f'Wrong result: {result.json}, '
        f'expected: {expected_result}'
    )
    assert 200 == result.status_code, (
        f'Wrong status code: {result.status_code}, '
        f'expected 200'
    )


@patch('requests.get')
def test_asset_calc_revenue_api_unavailable(mock_get, client):
    mock_get.return_value.status_code = 503
    expected_result = 'CBR service is unavailable'
    result = client.get('/cbr/key_indicators')
    mock_get.called_once(KEY_INDICATORS_URL)
    mock_get.called_once(DAILY_URL)
    assert 503 == result.status_code, (
        f'Wrong status_code: {result.status_code}, '
        f'expected: 503'
    )
    assert expected_result == result.data.decode(), (
        f'Wrong message: {result.data.decode()}, '
        f'expected: {expected_result}'
    )


def test_clear_api(client):
    client.application.bank = Storage([
        Asset('Diana', 5, 0, 'AMD'),
        Asset('Anya', 10, 1, 'USD'),
    ])
    result = client.get('/api/asset/cleanup')
    message = 'there are no more assets'
    banks_cnt = len(client.application.bank.asset_list)
    assert 200 == result.status_code, (
        f'Wrong status code: {result.status_code}, '
        f'expected 200'
    )
    assert message == result.data.decode(), (
        f'Wrong message: {result.data.decode()}, '
        f'expected {message}'
    )
    assert 0 == banks_cnt, (
        f'Wrong bank count: {banks_cnt}, '
        f'expected 0'
    )
