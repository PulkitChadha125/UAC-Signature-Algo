from datetime import datetime

from com.dakshata.autotrader.api.AutoTrader import AutoTrader

autotrader=None
# key="497f4ead-b710-4091-80ce-290205ed9f8a"

def login(key):
    autotrader = AutoTrader.create_instance(key, AutoTrader.SERVER_URL)
    return autotrader

def convert_date(date_str):
    date_obj = datetime.strptime(date_str, "%d-%b-%y")
    new_date_str = date_obj.strftime("%d-%b-%Y")
    return new_date_str


def regular_order(autotrader,account,segment,symbol,direction,orderType,productType,qty,price):
    response = autotrader.place_regular_order(account, segment, symbol,direction, orderType, productType, qty, price, 0.0)
    print(response)
