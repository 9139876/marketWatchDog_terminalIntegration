import json
import logging
import seqlog
import jsonpickle
from flask import Flask, request
from waitress import serve
from metatrader.mt5_manager import Mt5Manager
from auxiliary import web_helpers

app = Flask(__name__)

# region Terminal Info
terminal_info_controller = '/terminal-info'


@app.route(f'{terminal_info_controller}/version', methods=['GET'])
def get_version():
    def internal():
        dealer = request.args.get('dealerType')
        return json.dumps(mt5Manager.get(dealer).get_version())

    return web_helpers.execute(internal)


# endregion

# region Account info
account_info_controller = '/account-info'


@app.route(f'{account_info_controller}/get', methods=['GET'])
def get_account_info():
    def internal():
        dealer = request.args.get('dealerType')
        account_info_dirt = mt5Manager.get(dealer).get_account_info()
        account_info = web_helpers.dict_keys_modify(account_info_dirt, web_helpers.snake_to_lower_camel_case)
        return jsonpickle.encode(account_info, unpicklable=False)

    return web_helpers.execute(internal)


# endregion

# region Opened Positions
opened_positions_controller = '/opened-positions'


@app.route(f'{opened_positions_controller}/get', methods=['GET'])
def get_opened_positions():
    def internal():
        dealer = request.args.get('dealerType')
        opened_positions = mt5Manager.get(dealer).get_opened_positions()
        return jsonpickle.encode(opened_positions, unpicklable=False)

    return web_helpers.execute(internal)


# endregion

# region Symbol Info
symbol_info_controller = '/symbol-info'


@app.route(f'{symbol_info_controller}/get-symbols', methods=['GET'])
def get_symbols():
    def internal():
        dealer = request.args.get('dealerType')
        symbols = mt5Manager.get(dealer).get_symbols()
        return jsonpickle.encode(symbols, unpicklable=False)

    return web_helpers.execute(internal)


@app.route(f'{symbol_info_controller}/get-symbol-info', methods=['GET'])
def get_symbol_info():
    def internal():
        dealer = request.args.get('dealerType')
        symbol = request.args.get('symbol')
        symbol_info = mt5Manager.get(dealer).get_symbol_info(symbol)
        return jsonpickle.encode(symbol_info, unpicklable=False)

    return web_helpers.execute(internal)


# endregion

# region Position Management
position_management_controller = '/position_management'


@app.route(f'{position_management_controller}/update-stop-loss', methods=['POST'])
def update_stop_loss():
    def internal():
        data = request.get_json()
        dealer = data["dealerType"]
        identifier = int(data['identifier'])
        sl_value = float(data['stopLossValue'])

        result_dirt = mt5Manager.get(dealer).update_stop_loss(identifier, sl_value)
        result = web_helpers.dict_keys_modify(result_dirt, web_helpers.snake_to_lower_camel_case)

        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal)


@app.route(f'{position_management_controller}/close-position', methods=['POST'])
def close_position():
    def internal():
        dealer = request.args.get('dealerType')
        symbol = request.args.get('symbol')

        result_dirt = mt5Manager.get(dealer).close_position(symbol)
        result = web_helpers.dict_keys_modify(result_dirt, web_helpers.snake_to_lower_camel_case)

        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal)


@app.route(f'{position_management_controller}/open-position', methods=['POST'])
def open_position():
    def internal():
        data = request.get_json()
        dealer = data["dealerType"]
        symbol = data['symbol']
        action_str = data['action']
        volume = float(data['volume'])
        stop_loss = float(data['stopLoss'])

        result_dirt = mt5Manager.get(dealer).open_position(action_str, symbol, volume, stop_loss)
        result = web_helpers.dict_keys_modify(result_dirt, web_helpers.snake_to_lower_camel_case)

        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal)


# endregion

# region Quotes
quotes_controller = '/quotes'


@app.route(f'{quotes_controller}/get-last-quotes', methods=['POST'])
def get_last_quotes():
    def internal():
        data = request.get_json()
        dealer = data["dealerType"]
        symbols = data['symbols']
        timeframe = data['timeframe']
        count = int(data['count'])

        last_quotes = mt5Manager.get(dealer).get_last_quotes(symbols, timeframe, count)
        return jsonpickle.encode(last_quotes, unpicklable=False)

    return web_helpers.execute(internal)


@app.route(f'{quotes_controller}/get-quotes', methods=['POST'])
def get_quotes():
    def internal():
        data = request.get_json()
        dealer = data["dealerType"]
        symbol = data['symbol']
        timeframe = data['timeframe']
        count = int(data['count'])

        quotes = mt5Manager.get(dealer).get_quotes(symbol, timeframe, count)
        return jsonpickle.encode(quotes, unpicklable=False)

    return web_helpers.execute(internal)


# endregion

# region order_check

order_check_controller = '/order-check'


@app.route(f'{order_check_controller}/order-calc-profit', methods=['POST'])
def order_calc_profit():
    def internal():
        data = request.get_json()
        dealer = data["dealerType"]
        symbol = data['symbol']
        action_str = data['action']
        volume = float(data['volume'])
        price_open = float(data['priceOpen'])
        price_close = float(data['priceClose'])

        result = mt5Manager.get(dealer).order_calc_profit(action_str, symbol, volume, price_open, price_close)
        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal)


@app.route(f'{order_check_controller}/order-calc-margin', methods=['POST'])
def order_calc_margin():
    def internal():
        data = request.get_json()
        dealer = data["dealerType"]
        symbol = data['symbol']
        action_str = data['action']
        volume = float(data['volume'])
        price_open = float(data['priceOpen'])

        result = mt5Manager.get(dealer).order_calc_margin(action_str, symbol, volume, price_open)
        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal)


@app.route(f'{order_check_controller}/order-check', methods=['POST'])
def order_check():
    def internal():
        data = request.get_json()
        dealer = data["dealerType"]
        symbol = data['symbol']
        action_str = data['action']
        volume = float(data['volume'])
        stop_loss = float(data['stopLoss'])

        result_dirt = mt5Manager.get(dealer).order_check(action_str, symbol, volume, stop_loss)
        result = web_helpers.dict_keys_modify(result_dirt, web_helpers.snake_to_lower_camel_case)

        return jsonpickle.encode(result, unpicklable=False)

    return web_helpers.execute(internal)


# endregion

# configure loggers
seqlog.configure_from_file('./config/logConfig.yml')
seqlog.set_global_log_properties(application='metatrader_integration')

logger = logging.getLogger('main_logger')
mt5Manager = Mt5Manager()

serve(app, host="0.0.0.0", port=7100)
