import json
import logging
import os
import threading

import jsonpickle
from flask import Flask, request
from waitress import serve

from config import app_config
from auxiliary import web_helpers
from metatrader.auxiliary import datetime_str_to_unix_time
from metatrader.enums.mt5_dealer_type_enum import Mt5DealerTypeEnum
from metatrader.terminal_integration import MetaTrader5Integration
from monitoring.logger_callback_handler import CallbackHandler
from monitoring.monitoring_logger_callback import Monitoring

app = Flask(__name__)

# region Terminal Info
terminal_info_controller = '/terminal-info'


@app.route(f'{terminal_info_controller}/version', methods=['POST'])
def get_version():
    def internal():
        return json.dumps(mt5.get_version())

    return web_helpers.execute(internal, mt5)


# endregion

# region Account info
account_info_controller = '/account-info'


@app.route(f'{account_info_controller}/get', methods=['POST'])
def get_account_info():
    def internal():
        __dealer_validate__(request)

        account_info_dirt = mt5.get_account_info()
        account_info = web_helpers.dict_keys_modify(account_info_dirt, web_helpers.snake_to_lower_camel_case)
        return jsonpickle.encode(account_info, unpicklable=False)

    return web_helpers.execute(internal, mt5)


# endregion

# region Opened Positions
opened_positions_controller = '/opened-positions'


@app.route(f'{opened_positions_controller}/get', methods=['POST'])
def get_opened_positions():
    def internal():
        __dealer_validate__(request)

        opened_positions = mt5.get_opened_positions()
        return jsonpickle.encode(opened_positions, unpicklable=False)

    return web_helpers.execute(internal, mt5)


# endregion

# region Symbol Info
symbol_info_controller = '/symbol-info'


@app.route(f'{symbol_info_controller}/get-symbols', methods=['POST'])
def get_symbols():
    def internal():
        __dealer_validate__(request)

        symbols_dirt = mt5.get_symbols()
        symbols = list(map(lambda x: web_helpers.dict_keys_modify(x, web_helpers.snake_to_lower_camel_case), symbols_dirt))

        return jsonpickle.encode(symbols, unpicklable=False)

    return web_helpers.execute(internal, mt5)


@app.route(f'{symbol_info_controller}/get-symbol-info', methods=['POST'])
def get_symbol_info():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        symbol = data['symbol']

        symbol_info_dirt = mt5.get_symbol_info(symbol)
        symbol_info = web_helpers.dict_keys_modify(symbol_info_dirt, web_helpers.snake_to_lower_camel_case)
        return jsonpickle.encode(symbol_info, unpicklable=False)

    return web_helpers.execute(internal, mt5)


@app.route(f'{symbol_info_controller}/get-symbols-rating', methods=['GET'])
def get_symbol_rating():
    def internal():
        symbols = mt5.get_symbols()
        ratings = []

        for symbol in symbols:
            price = (symbol['ask'] + symbol['bid']) / 2

            if price == 0:
                continue

            spread = symbol['spread']
            point = symbol['point']
            digits = symbol['digits']
            name = symbol['name']
            spread_div_price = 100 * spread * point / price

            ratings.append({'name': name, 'spreadDivPrice': round(spread_div_price, 2), 'spread': spread, 'price': round(price, digits)})

        ratings = sorted(ratings, key=lambda item: item['spreadDivPrice'])

        return jsonpickle.encode(ratings, unpicklable=False)

    return web_helpers.execute(internal, mt5)


# endregion

# region Position Management
position_management_controller = '/position_management'


@app.route(f'{position_management_controller}/update-stop-loss', methods=['POST'])
def update_stop_loss():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        identifier = int(data['identifier'])
        sl_value = float(data['stopLossValue'])

        result_dirt = mt5.update_stop_loss(identifier, sl_value)
        result = web_helpers.dict_keys_modify(result_dirt, web_helpers.snake_to_lower_camel_case)

        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal, mt5)


@app.route(f'{position_management_controller}/close-position', methods=['POST'])
def close_position():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        symbol = data['symbol']

        result = mt5.close_position(symbol)

        if result is True:
            return '{ }'

        raise Exception('Unknown error')

    return web_helpers.execute(internal, mt5)


@app.route(f'{position_management_controller}/open-position', methods=['POST'])
def open_position():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        symbol = data['symbol']
        action_str = data['action']
        volume = float(data['volume'])
        stop_loss = float(data['stopLoss'])

        result_dirt = mt5.open_position(action_str, symbol, volume, stop_loss)
        result = web_helpers.dict_keys_modify(result_dirt, web_helpers.snake_to_lower_camel_case)

        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal, mt5)


# endregion

# region Quotes
quotes_controller = '/quotes'


@app.route(f'{quotes_controller}/get-last-quotes', methods=['POST'])
def get_last_quotes():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        symbols = data['symbols']
        timeframe = data['timeframe']
        count = int(data['count'])

        last_quotes = mt5.get_last_quotes(symbols, timeframe, count)
        return jsonpickle.encode(last_quotes, unpicklable=False)

    return web_helpers.execute(internal, mt5)


@app.route(f'{quotes_controller}/get-quotes', methods=['POST'])
def get_quotes():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        symbol = data['symbol']
        timeframe = data['timeframe']
        count = int(data['count'])

        quotes = mt5.get_quotes(symbol, timeframe, count)
        return jsonpickle.encode(quotes, unpicklable=False)

    return web_helpers.execute(internal, mt5)


@app.route(f'{quotes_controller}/get-range-quotes', methods=['POST'])
def get_range_quotes():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        symbol = data['symbol']
        timeframe = data['timeframe']
        date_from = datetime_str_to_unix_time(data['dateFrom'])
        date_to = datetime_str_to_unix_time(data['dateTo'])

        quotes = mt5.get_range_quotes(symbol, timeframe, date_from, date_to)
        return jsonpickle.encode(quotes, unpicklable=False)

    return web_helpers.execute(internal, mt5)


# endregion

# region order_check

order_check_controller = '/order-check'


@app.route(f'{order_check_controller}/order-calc-profit', methods=['POST'])
def order_calc_profit():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        symbol = data['symbol']
        action_str = data['action']
        volume = float(data['volume'])
        price_open = float(data['priceOpen'])
        price_close = float(data['priceClose'])

        result = mt5.order_calc_profit(action_str, symbol, volume, price_open, price_close)
        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal, mt5)


@app.route(f'{order_check_controller}/order-calc-margin', methods=['POST'])
def order_calc_margin():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        symbol = data['symbol']
        action_str = data['action']
        volume = float(data['volume'])
        price_open = float(data['priceOpen'])

        result = mt5.order_calc_margin(action_str, symbol, volume, price_open)
        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal, mt5)


@app.route(f'{order_check_controller}/order-check', methods=['POST'])
def order_check():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        symbol = data['symbol']
        action_str = data['action']
        volume = float(data['volume'])
        stop_loss = float(data['stopLoss'])

        result_dirt = mt5.order_check(action_str, symbol, volume, stop_loss)
        result = web_helpers.dict_keys_modify(result_dirt, web_helpers.snake_to_lower_camel_case)

        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal, mt5)


# endregion

# region history

get_history_controller = '/get-history'


@app.route(f'{get_history_controller}/get-history-deals', methods=['POST'])
def history_deals_get():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        date_from = datetime_str_to_unix_time(data['dateFrom'])

        result = mt5.history_deals_get(date_from)

        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal, mt5)


@app.route(f'{get_history_controller}/get-history-orders', methods=['POST'])
def history_orders_get():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        date_from = datetime_str_to_unix_time(data['dateFrom'])

        result_dirt = mt5.history_orders_get(date_from)
        result = list(map(lambda x: web_helpers.dict_keys_modify(x, web_helpers.snake_to_lower_camel_case), result_dirt))

        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal, mt5)


# endregion

# region private

def __dealer_validate__(_request: request):
    data = _request.get_json()
    dealer = data['dealerType']

    if Mt5DealerTypeEnum[dealer] != current_dealer:
        raise Exception(f'Invalid dealer - current dealer is {current_dealer}, but requested {dealer}')


# endregion

# configure application
import sys

if len(sys.argv) < 4:
    raise Exception("Required args (dealer, port, environment) not specified")

dealer_str = sys.argv[1]
current_dealer = Mt5DealerTypeEnum[dealer_str]
port = int(sys.argv[2])
env = sys.argv[3]

login = int(os.environ.get(f'{dealer_str}_Login_{env}'))
password = os.environ.get(f'{dealer_str}_Password_{env}')
server = os.environ.get(f'{dealer_str}_Server_{env}')

# logger
# В мониторинг отправка через SendLog JSON из logger callback
logger = logging.getLogger(f'{dealer_str}_{env}_logger')
logger.setLevel(logging.DEBUG)

# Обработчик для консоли
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Обработчик для файла
file_handler = logging.FileHandler(f'{dealer_str}_{env}.log', encoding="utf-8")
file_handler.setLevel(logging.INFO)

# Форматировщик (одинаковый для обоих)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(console_handler)
logger.addHandler(file_handler)

mt5: MetaTrader5Integration

if current_dealer == Mt5DealerTypeEnum.AlfaForex:
    mt5 = MetaTrader5Integration(app_config.ALPHA_FOREX_METATRADER_PATH, login, password, server, logger)
elif current_dealer == Mt5DealerTypeEnum.Finam:
    mt5 = MetaTrader5Integration(app_config.FINAM_METATRADER_PATH, login, password, server, logger)
else:
    raise Exception(f'Invalid dealer \'{sys.argv[1]}\'')

# Обработчик для мониторинга
def empty_task(_mt5: MetaTrader5Integration):
    pass

i_am_alive_task = empty_task

use_monitoring_str = os.environ.get('UseMonitoring')
use_monitoring = True if use_monitoring_str == '1' else False

if use_monitoring:
    server_url = os.environ.get('MonitoringServerUrl')
    monitoring_secret_key = os.environ.get('MonitoringSecretKey')
    component_id = os.environ.get(f'IntegrationComponentId_{dealer_str}_{env}')
    unit_test_id = os.environ.get(f'IntegrationUnitTestId_{dealer_str}_{env}')

    monitoring = Monitoring(server_url, monitoring_secret_key, component_id, unit_test_id)
    monitoring_handler = CallbackHandler(monitoring.logger_callback)
    logger.addHandler(monitoring_handler)

    # IAmAlive
    i_am_alive_task = monitoring.send_i_am_alive

def schedule_next_run(interval_seconds: int):
    def wrapper():
        try:
            i_am_alive_task(mt5)
        finally:
            # Планируем следующий запуск
            threading.Timer(interval_seconds, wrapper).start()
    wrapper()

logger.info(f'Application running for dealer \'{current_dealer}\' on port {port}')

schedule_next_run(30)

# 1 поток, максимум 200 ожидающих соединений - может жестко жрать ресурсы и тупить - проверить
serve(app, host="0.0.0.0", port=port, threads=1, connection_limit=200)
