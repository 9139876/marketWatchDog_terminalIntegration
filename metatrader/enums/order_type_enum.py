import enum


class Metatrader5OrderTypeEnum(enum.Enum):
    ORDER_TYPE_BUY = 0  # Market Buy order
    ORDER_TYPE_SELL = 1  # Market Sell order
    ORDER_TYPE_BUY_LIMIT = 2  # Buy Limit pending order
    ORDER_TYPE_SELL_LIMIT = 3  # Sell Limit pending order
    ORDER_TYPE_BUY_STOP = 4  # Buy Stop pending order
    ORDER_TYPE_SELL_STOP = 5  # Sell Stop pending order
    ORDER_TYPE_BUY_STOP_LIMIT = 6  # Upon reaching the order price, a pending Buy Limit order is placed at the StopLimit price
    ORDER_TYPE_SELL_STOP_LIMIT = 7  # Upon reaching the order price, a pending Sell Limit order is placed at the StopLimit price
    ORDER_TYPE_CLOSE_BY = 8  # Order to close a position by an opposite one
