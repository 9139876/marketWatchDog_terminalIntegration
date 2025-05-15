import json
import logging
import seqlog
import jsonpickle
from flask import Flask, request
from waitress import serve
from config import app_config
from metatrader.terminal_integration import MetaTrader5Integration
from auxiliary.web_helpers import execute

app = Flask(__name__)

# region Terminal Info
terminal_info_controller = '/terminal-info'


@app.route(f'{terminal_info_controller}/version', methods=['GET'])
def get_version():
    return json.dumps(mt5.get_version())


# endregion

# region Opened Positions
opened_positions_controller = '/opened-positions'


@app.route(f'{opened_positions_controller}/get', methods=['GET'])
def get_opened_positions():
    opened_positions = mt5.get_opened_positions()
    return jsonpickle.encode(opened_positions, unpicklable=False)


# endregion

# region Symbol Info
symbol_info_controller = '/symbol-info'


@app.route(f'{symbol_info_controller}/get-symbol-info', methods=['GET'])
def get_symbol_info():
    symbol = request.args.get('symbol')
    symbol_info = mt5.get_symbol_info(symbol)
    return jsonpickle.encode(symbol_info, unpicklable=False)


# endregion

# region Position Management
position_management_controller = '/position_management'


@app.route(f'{position_management_controller}/update-stop-loss', methods=['POST'])
def update_stop_loss():
    data = request.get_json()
    identifier = int(data['identifier'])
    sl_value = float(data['stopLossValue'])
    mt5.update_stop_loss(identifier, sl_value)


@app.route(f'{position_management_controller}/close-position', methods=['POST'])
def close_position():
    symbol = request.args.get('symbol')
    mt5.close_position(symbol)


# endregion

# region Position Management
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

    return execute(internal)


# endregion


# configure loggers
seqlog.configure_from_file('./config/logConfig.yml')
seqlog.set_global_log_properties(application='metatrader_integration')

logger = logging.getLogger('main_logger')
mt5 = MetaTrader5Integration(app_config.ALPHA_FOREX_METATRADER_PATH, logging.getLogger('mt5_logger'))

serve(app, host="0.0.0.0", port=7100)
