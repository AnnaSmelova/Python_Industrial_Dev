#!/usr/bin/env python3
"""
Web service for Asset
"""
import bisect
from typing import Any, Dict, List, Union

import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, jsonify, make_response, request


DAILY_URL = 'https://www.cbr.ru/eng/currency_base/daily/'
KEY_INDICATORS_URL = 'https://www.cbr.ru/eng/key-indicators/'


class Asset:
    """
    Asset class
    """
    def __init__(self, name: str, capital: float, interest: float, char_code: str):
        """
        Initialization
        :param name: name
        :param capital: capital
        :param interest: interest
        :param char_code: currency
        """
        self.name = name
        self.capital = capital
        self.interest = interest
        self.char_code = char_code

    def calculate_revenue(self, years: int) -> float:
        """
        Calculate revenue function
        :param years: years
        :return: revenue
        """
        revenue = self.capital * ((1.0 + self.interest) ** years - 1.0)
        return revenue

    def get_json(self):
        """
        Get JSON function
        :return: json
        """
        return [
            self.char_code,
            self.name,
            self.capital,
            self.interest
        ]

    def __repr__(self):
        repr_ = f'{self.__class__.__name__}({self.name}, {self.capital}, {self.interest}, {self.char_code})'
        return repr_

    def __lt__(self, other) -> bool:
        """
        less than operator
        :param other: right value
        :return: result of compare
        """
        if isinstance(other, Asset):
            return self.name < other.name
        raise ValueError(f'Can not compare Asset and {other.__class__.__name__}')


class Storage:
    """Class for storing assets"""

    def __init__(self, asset_list: Union[List[Asset], None] = None):
        """
        Storage init
        :param asset_list: list of assets
        """
        self.asset_list = []
        if asset_list:
            for item in asset_list:
                bisect.insort_left(self.asset_list, item)

    def add_asset(self, item: Asset):
        """
        Add asset to storage
        :return: Nothing
        """
        bisect.insort_left(self.asset_list, item)

    def is_contains(self, item: Asset) -> bool:
        """
        Check do asset contains in list
        :param item: asset
        :return: True if contains else False
        """
        i = bisect.bisect_left(self.asset_list, item)
        if len(self.asset_list) != i and item.name == self.asset_list[i].name:
            return True
        return False

    def get_json(self) -> List[List[Any]]:
        """
        Get json repr
        :return: list of repr
        """
        result = []
        for item in self.asset_list:
            bisect.insort_left(result, item.get_json())
        return result

    def clear_storage(self):
        """
        Clear storage
        :return: Nothing
        """
        self.asset_list.clear()

    def get_assets(self, name: str) -> List[Any]:
        """
        Method to get asset list repr by name
        :param name: asset name
        :return: list repr
        """
        i = bisect.bisect_left(self.asset_list, Asset(name, 0, 0, 'US'))
        if i != len(self.asset_list) and self.asset_list[i].name == name:
            return self.asset_list[i].get_json()
        return []

    def get_total_revenue(self, period: int,
                          key_indicator: Dict[str, float],
                          daily: Dict[str, float]) -> float:
        """
        Calculate total revenue by mapping of key_interest map and daily map
        :param period: period for revenue
        :param key_indicator: mapping of char code to currency value
        :param daily: mapping of char code to currency value
        :return: Total revenue of storage
        """
        result = 0
        for item in self.asset_list:
            if item.char_code in key_indicator:
                mapping = key_indicator[item.char_code]
            else:
                mapping = daily[item.char_code]
            result += item.calculate_revenue(period) * mapping
        return result


app = Flask(__name__)
app.bank = Storage()


def custom_float(string: str) -> float:
    """
    Convert string from to float
    :param string: string
    :return: float
    """
    return float(string.replace(',', ''))


def parse_cbr_currency_base_daily(html_data: str) -> Dict[str,float]:
    """
    Parse https://www.cbr.ru/eng/currency_base/daily/
    :param html_data: page content
    :return: mapping of char code to one unit price
    """
    result = {}
    #result['RUB'] = custom_float('1')
    parsed = BeautifulSoup(html_data, 'html.parser')
    table = parsed.find('table', attrs={'class': 'data'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 5:
            result[cols[1].text] = custom_float(cols[4].text) / custom_float(cols[2].text)
    return result


def parse_cbr_key_indicators(html_data: str) -> Dict[str,float]:
    """
    Parse https://www.cbr.ru/eng/key-indicators/
    :param html_data: page content
    :return: mapping of char code to one unit price
    """
    result = {}
    parsed = BeautifulSoup(html_data, 'html.parser')
    div_tables = parsed.find_all('div', attrs={'class': 'table key-indicator_table'})
    #for div_table in div_tables[1:3]:
    for div_table in div_tables[:2]:
        rows = div_table.findAll('tr')
        for row in rows[1:]:
            char_code = row.find('div',
                                 attrs={'class': 'col-md-3 offset-md-1 _subinfo'}).text
            value = custom_float(row.findAll('td')[-1].text)
            result[char_code] = value
    return result


@app.route('/cbr/daily')
def cbr_daily_api() -> Response:
    """
    Get currency mapping from https://www.cbr.ru/eng/currency_base/daily/
    :return: JSON
    """
    response = requests.get(DAILY_URL)
    result = parse_cbr_currency_base_daily(response.text)
    return jsonify(result)


@app.route('/cbr/key_indicators')
def cbr_interest_key_api() -> Response:
    """
    Get currency mapping from https://www.cbr.ru/eng/key-indicators/
    :return: JSON
    """
    response = requests.get(KEY_INDICATORS_URL)
    result = parse_cbr_key_indicators(response.text)
    return jsonify(result)


@app.errorhandler(404)
def page_not_found(e) -> Response:
    """
    404 error
    :return: response for 404 page
    """
    return make_response('This route is not found', 404)


@app.errorhandler(500)
def cbr_unavailable(e) -> Response:
    """
    503 error
    :return: response for 503 page
    """
    return make_response('CBR service is unavailable', 503)


@app.route('/api/asset/add/<string:char_code>/<string:name>/<string:capital>/<string:interest>')
def add_asset_api(char_code: str, name: str, capital: str, interest: str) -> Response:
    """
    Add asset
    :param char_code: char code
    :param name: name
    :param capital: capital
    :param interest: interest
    :return: 200 if asset not exist else 403
    """
    asset = Asset(
        char_code=char_code,
        name=name,
        capital=float(capital),
        interest=float(interest)
    )
    if app.bank.is_contains(asset):
        return make_response('Name has already exist', 403)
    app.bank.add_asset(asset)
    return make_response(f"Asset '{name}' was successfully added", 200)


@app.route('/api/asset/list')
def asset_list_api():
    """
    Api to get asset list
    :return: JSON of asset list
    """
    data = app.bank.get_json()
    return jsonify(data)


@app.route('/api/asset/get')
def asset_get_api():
    """
    Api to get asset from list by names
    :return: JSON of asset list
    """
    data = []
    names = request.args.getlist('name')
    for name in names:
        asset = app.bank.get_assets(name)
        if asset:
            data.append(asset)
    return jsonify(sorted(data))


@app.route('/api/asset/calculate_revenue')
def asset_calc_revenue_api():
    """
    Api to calculate revenue
    :return: JSON of dict period to revenue
    """
    data = {}
    periods = request.args.getlist('period')
    cbr_indicator_response = requests.get(KEY_INDICATORS_URL)
    cbr_daily_response = requests.get(DAILY_URL)
    indicator_map = parse_cbr_key_indicators(cbr_indicator_response.text)
    daily_map = parse_cbr_currency_base_daily(cbr_daily_response.text)
    daily_map['RUB'] = custom_float('1')
    for period in periods:
        data[int(period)] = app.bank.get_total_revenue(
            period=int(period),
            key_indicator=indicator_map,
            daily=daily_map)
    return jsonify(data)


@app.route('/api/asset/cleanup')
def clear_api():
    """
    Api for clear storage
    :return: 200
    """
    app.bank.clear_storage()
    return make_response('there are no more assets', 200)
