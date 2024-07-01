AppName="5P50464027"
AppSource=22187
UserID="3bbhuGGYiGo"
Password="kLyjsnYBl3s"
UserKey="gTmPXuRKttC7V8piLAwtcMp7gRoaHyfW"
EncryptionKey="eFO2bZ3jT0AnCjFHFO5CzFBxjzedbWxc"
Validupto="3/30/2050 12:00:00 PM"
Redirect_URL="Null"
totpstr="GUYDINRUGAZDOXZVKBDUWRKZ"

from datetime import datetime,timedelta
from py5paisa import FivePaisaClient
import pyotp
import pandas as pd
client=None

def login():
    global client
    cred={
        "APP_NAME":AppName,
        "APP_SOURCE":AppSource,
        "USER_ID":UserID,
        "PASSWORD":Password,
        "USER_KEY":UserKey,
        "ENCRYPTION_KEY":EncryptionKey
        }
    twofa = pyotp.TOTP(totpstr)
    twofa = twofa.now()
    client = FivePaisaClient(cred=cred)
    client.get_totp_session(client_code=50464027,totp=twofa,pin=123456)
    client.get_oauth_session('Your Response Token')
    print(client.get_access_token())

def round_down_to_interval(dt, interval_minutes):
    remainder = dt.minute % interval_minutes
    minutes_to_current_boundary = remainder

    rounded_dt = dt - timedelta(minutes=minutes_to_current_boundary)

    rounded_dt = rounded_dt.replace(second=0, microsecond=0)

    return rounded_dt

def determine_min(minstr):
    min = 0
    if minstr == "1m":
        min = 1
    if minstr == "3m":
        min = 3
    if minstr == "5m":
        min = 5
    if minstr == "15m":
        min = 15
    if minstr == "30m":
        min = 30

    return min
def get_historical_data(timframe, token,symbol):
    global client
    current_time = datetime.now()
    if timframe == "1m":
        delta_minutes = 1
        delta_minutes2 = 2
    elif timframe == "3m":
        delta_minutes = 3
        delta_minutes2 = 6
    elif timframe == "5m":
        delta_minutes = 5
        delta_minutes2 = 10
    elif timframe == "15m":
        delta_minutes = 15
        delta_minutes2 = 30

    next_specific_part_time = datetime.now() - timedelta(
        seconds=determine_min(timframe) * 60)
    desired_time_str1 = round_down_to_interval(next_specific_part_time,
                                                     determine_min(timframe))
    desired_time_str2=desired_time_str1- timedelta(
        seconds=determine_min(timframe) * 60)

    from_time = datetime.now() - timedelta(days=6)
    to_time = datetime.now()
    df = client.historical_data('N', 'D', token, timframe, from_time, to_time)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    df.reset_index(inplace=True)
    df['Datetime'] = df['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')


    # if symbol=="NIFTY":
    #     df.to_csv('NIFTY.csv', index=False)
    # if symbol=="BANKNIFTY":
    #     df.to_csv('BANKNIFTY.csv', index=False)

    last_3_rows = df.tail(3)
    desired_rows = last_3_rows[
        (pd.to_datetime(last_3_rows['Datetime']) == desired_time_str1) |
        (pd.to_datetime(last_3_rows['Datetime']) == desired_time_str2)
        ]
    return desired_rows



def get_live_market_feed(CallToken):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "D", "ScripData": CallToken}]
    print(req_list_)
    print(client.fetch_market_feed_scrip(req_list_))

def previousdayclose(code):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "D", "ScripCode": code}]
    responce=client.fetch_market_feed_scrip(req_list_)
    pclose_value = float(responce['Data'][0]['PClose'])
    return pclose_value

def get_open_current_candle(code):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "D", "ScripCode": code}]
    responce = client.Request_Feed("mf","s",req_list_)
    print(responce)
    return responce


def get_ltp(code):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "D", "ScripCode": code}]
    responce=client.fetch_market_feed_scrip(req_list_)
    last_rate = float(responce['Data'][0].get('LastRate', 0))
    return last_rate

def buy( ScripCode , Qty, Price,OrderType='B',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def sell( ScripCode , Qty, Price,OrderType='S',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)
def short( ScripCode , Qty, Price,OrderType='S',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def cover( ScripCode , Qty, Price,OrderType='B',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def get_position():
    global client
    responce = client.positions()

    return responce

def get_margin():
    global client
    responce= client.margin()

    if responce:
        net_available_margin =float (responce[0]['NetAvailableMargin'])
        return net_available_margin
    else:
        print("Error: Unable to get NetAvailableMargin")
        return None


def get_active_expiery(symbol):
    response = client.get_expiry("N", symbol)
    expiry_dates = []

    for expiry in response['Expiry']:
        expiry_date_string = expiry['ExpiryDate']
        expiry_date_numeric = int(expiry_date_string.split("(")[1].split("+")[0]) / 1000
        epoch = datetime(1970, 1, 1)
        expiry_datetime = epoch + timedelta(seconds=expiry_date_numeric)
        expiry_date = expiry_datetime.strftime('%Y-%m-%d')
        expiry_dates.append(expiry_date)

    return expiry_dates



















