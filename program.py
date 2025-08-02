import json
import logging
import seqlog
import jsonpickle
from flask import Flask, request
from waitress import serve
from config import app_config
from metatrader.terminal_integration import MetaTrader5Integration
from auxiliary import web_helpers

app = Flask(__name__)

# region Terminal Info
terminal_info_controller = '/terminal-info'


@app.route(f'{terminal_info_controller}/version', methods=['GET'])
def get_version():
    def internal():
        return json.dumps(mt5.get_version())

    return web_helpers.execute(internal)


# endregion

# region Account info
account_info_controller = '/account-info'

@app.route(f'{account_info_controller}/get', methods=['GET'])
def get_account_info():
    def internal():
        account_info_dirt = mt5.get_account_info()
        account_info = web_helpers.dict_keys_modify(account_info_dirt, web_helpers.snake_to_lower_camel_case)
        return jsonpickle.encode(account_info, unpicklable=False)

    return web_helpers.execute(internal)
# endregion

# region Opened Positions
opened_positions_controller = '/opened-positions'


@app.route(f'{opened_positions_controller}/get', methods=['GET'])
def get_opened_positions():
    def internal():
        opened_positions = mt5.get_opened_positions()
        return jsonpickle.encode(opened_positions, unpicklable=False)

    return web_helpers.execute(internal)


# endregion

# region Symbol Info
symbol_info_controller = '/symbol-info'

@app.route(f'{symbol_info_controller}/get-symbols', methods=['GET'])
def get_symbols():
    def internal():
        symbols = mt5.get_symbols()
        return jsonpickle.encode(symbols, unpicklable=False)

    return web_helpers.execute(internal)

@app.route(f'{symbol_info_controller}/get-symbol-info', methods=['GET'])
def get_symbol_info():
    def internal():
        symbol = request.args.get('symbol')
        symbol_info = mt5.get_symbol_info(symbol)
        return jsonpickle.encode(symbol_info, unpicklable=False)

    return web_helpers.execute(internal)


# endregion

# region Position Management
position_management_controller = '/position_management'


@app.route(f'{position_management_controller}/update-stop-loss', methods=['POST'])
def update_stop_loss():
    def internal():
        data = request.get_json()
        identifier = int(data['identifier'])
        sl_value = float(data['stopLossValue'])
        mt5.update_stop_loss(identifier, sl_value)

    return web_helpers.execute(internal)


@app.route(f'{position_management_controller}/close-position', methods=['POST'])
def close_position():
    def internal():
        symbol = request.args.get('symbol')
        mt5.close_position(symbol)

    return web_helpers.execute(internal)

@app.route(f'{position_management_controller}/open-position', methods=['POST'])
def open_position():
    def internal():
        data = request.get_json()
        order_type_str = data['orderType']
        symbol = data['symbol']
        volume = float(data['volume'])

        result = mt5.open_position(order_type_str, symbol, volume)

    return web_helpers.execute(internal)

# endregion

# region Quotes
quotes_controller = '/quotes'


@app.route(f'{quotes_controller}/get-last-quotes', methods=['POST'])
def get_last_quotes():
    def internal():
        data = request.get_json()
        symbols = data['symbols']
        timeframe = data['timeframe']
        count = int(data['count'])

        last_quotes = mt5.get_last_quotes(symbols, timeframe, count)
        return jsonpickle.encode(last_quotes, unpicklable=False)

    return web_helpers.execute(internal)


# endregion

# region order_check

order_check_controller = '/order-check'

@app.route(f'{order_check_controller}/order-calc-profit', methods=['POST'])
def order_calc_profit():
    def internal():
        data = request.get_json()
        action_str = data['action']
        symbol = data['symbol']
        volume = float(data['volume'])
        price_open = float(data['priceOpen'])
        price_close = float(data['priceClose'])

        order_profit = mt5.order_calc_profit(action_str, symbol, volume, price_open, price_close)

        if order_profit is None:
            raise Exception('No order profit found')

        return jsonpickle.encode(order_profit, unpicklable=False)

    return web_helpers.execute(internal)

# endregion

# configure loggers
seqlog.configure_from_file('./config/logConfig.yml')
seqlog.set_global_log_properties(application='metatrader_integration')

logger = logging.getLogger('main_logger')
mt5 = MetaTrader5Integration(app_config.ALPHA_FOREX_METATRADER_PATH, logging.getLogger('mt5_logger'))

serve(app, host="0.0.0.0", port=7100)
