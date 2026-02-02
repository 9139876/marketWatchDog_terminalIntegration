import json
import logging

import seqlog
import jsonpickle
from flask import Flask, request
from waitress import serve

from config import app_config
from auxiliary import web_helpers
from metatrader.models.mt5DealerTypeEnum import Mt5DealerTypeEnum
from metatrader.terminal_integration import MetaTrader5Integration

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
        date_from = int(data['dateFrom'])
        date_to = int(data['dateTo'])

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
        date_from = int(data['dateFrom'])

        result_dirt = mt5.history_deals_get(date_from)
        result = list(map(lambda x: web_helpers.dict_keys_modify(x, web_helpers.snake_to_lower_camel_case), result_dirt))

        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal, mt5)


@app.route(f'{get_history_controller}/get-history-orders', methods=['POST'])
def history_orders_get():
    def internal():
        __dealer_validate__(request)

        data = request.get_json()
        date_from = int(data['dateFrom'])

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

seqlog.configure_from_file('./config/logConfig.yml')
logger = logging.getLogger('main_logger')

if len(sys.argv) < 3:
    raise Exception("Required args (dealer and port) not specified")

current_dealer = Mt5DealerTypeEnum[sys.argv[1]]
port = int(sys.argv[2])

mt5: MetaTrader5Integration

if current_dealer == Mt5DealerTypeEnum.AlfaForex:
    mt5 = MetaTrader5Integration(app_config.ALPHA_FOREX_METATRADER_PATH, logging.getLogger('mt5_alfa_forex_logger'))
elif current_dealer == Mt5DealerTypeEnum.Finam:
    mt5 = MetaTrader5Integration(app_config.FINAM_METATRADER_PATH, logging.getLogger('mt5_finam_logger'))
else:
    raise Exception(f'Invalid dealer \'{sys.argv[1]}\'')

logger.info(f'Application stared for dealer \'{current_dealer}\' on port {port}')

# 1 поток, максимум 200 ожидающих соединений - может жестко жрать ресурсы и тупить - проверить
serve(app, host="0.0.0.0", port=port, threads=1, connection_limit=200)
