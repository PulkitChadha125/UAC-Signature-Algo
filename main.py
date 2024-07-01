import  FivePaisaIntegration,Stockdeveloper
import time
import traceback
import pandas as pd
from pathlib import Path
import pyotp
from datetime import datetime, timedelta, timezone

print(f"Strategy developed by Programetix visit link for more development requirements : {'https://programetix.com/'} ")



def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_zerodha_credentials():
    delete_file_contents("OrderLog.txt")
    # delete_file_contents("C:\\Users\\Administrator\\OneDrive\\Desktop\\RaviSptrendRsiVwap-master\\RaviSptrendRsiVwap-master\\OrderLog.txt")
    credentials = {}
    try:
        df = pd.read_csv('MainSettings.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials

credentials_dict = get_zerodha_credentials()






stockdevaccount=credentials_dict.get('stockdevaccount')

# Stockdeveloper.regular_order(account=stockdevaccount,segment="NSE",symbol="NIFTY_13-JUN-2024_CE_22700",direction="BUY"
#                                              ,orderType="MARKET",productType='INTRADAY',qty=25,price=200)


def custom_round(price, symbol):
    rounded_price = None
    if symbol == "NIFTY":
        last_two_digits = price % 100
        if last_two_digits < 25:
            rounded_price = (price // 100) * 100
        elif last_two_digits < 75:
            rounded_price = (price // 100) * 100 + 50
        else:
            rounded_price = (price // 100 + 1) * 100
            return rounded_price

    elif symbol == "BANKNIFTY":
        last_two_digits = price % 100
        if last_two_digits < 50:
            rounded_price = (price // 100) * 100
        else:
            rounded_price = (price // 100 + 1) * 100
        return rounded_price

    else:
        pass

    return rounded_price


def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')

result_dict = {}
client_dict={}
def get_client_detail():
    global client_dict
    try:
        csv_path = 'clientdetails.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}

        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            symbol_dict = {
                'Title': row['Title'],
                'Value': row['Value'],
                'NiftyQtyMultiplier': row['NiftyQtyMultiplier'],
                'Bankniftyultiplier': row['Bankniftyultiplier'],
                'autotrader': None,
            }
            client_dict[row['Title']] = symbol_dict
        # print("client_dict: ", client_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))


get_client_detail()


def stock_dev_login_multiclient(client_dict):
    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):
            daram['autotrader']=Stockdeveloper.login(daram['Value'])
    print("client_dict: ",client_dict)




stock_dev_login_multiclient(client_dict)

# buy
def stockdev_multiclient_orderplacement_buy(basesymbol,client_dict,timestamp,symbol,direction,Stoploss,Target,qty,price, side):
    Orderqty=None
    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):
            if basesymbol=="NIFTY":
                Orderqty=qty*daram['NiftyQtyMultiplier']
            if basesymbol=="BANKNIFTY":
                Orderqty=qty*daram['Bankniftyultiplier']


            Stockdeveloper.regular_order(autotrader=daram["autotrader"],account=daram['Title'], segment="NSE", symbol=symbol,
                                         direction=direction
                                         , orderType="MARKET", productType='INTRADAY', qty=Orderqty,
                                         price=price)
            orderlog = (
                f"{timestamp} Buy Order executed {side} side {symbol} @  {price},stoploss= {Stoploss}, "
                f"target= {Target} : Account = {daram['Title']} ")
            print(orderlog)
            write_to_order_logs(orderlog)

# exit
def stockdev_multiclient_orderplacement_exit(basesymbol,client_dict,timestamp,symbol,direction,Stoploss,Target,qty,price,log):
    Orderqty = None
    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):
            if basesymbol=="NIFTY":
                Orderqty=qty*daram['NiftyQtyMultiplier']
            if basesymbol=="BANKNIFTY":
                Orderqty=qty*daram['Bankniftyultiplier']
            Stockdeveloper.regular_order(autotrader=daram["autotrader"],account=daram['Title'], segment="NSE", symbol=symbol,
                                         direction=direction
                                         , orderType="MARKET", productType='INTRADAY', qty=Orderqty,
                                         price=price)
            orderlog = (
                f"{timestamp} {log} {symbol} @  {price} "
                f"target= {Target} : Account = {daram['Title']} ")
            print(orderlog)
            write_to_order_logs(orderlog)


def get_user_settings():
    global result_dict
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}

        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            symbol_dict = {
                'Symbol': row['Symbol'],
                'Timeframe': row['Timeframe'],
                'Quantity': row['Quantity'],
                'Expiery': row['Expiery'],
                'TradeExp':row['TradeExp'],
                "EntryPercentage": float(row['EntryPercentage']),
                "SlBufferPts": float(row['SlBufferPts']),
                "OptionRange": float(row['OptionRange']),
                "putstrike":None,"callstrike":None,
                "runonce": False,
                "CallToken": None,
                "PutToken": None,
                "BuyCall": None,
                "BuyPut": None,
                "CallLow": None,
                "PutLow": None,
                "strikeStep":int(row['strikeStep']),
                "Trade":None,"Stoploss":None,"Target":None,"callSymbol":None,"putSymbol":None,"TradeDisable":True

            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))


get_user_settings()



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

def find_scrip_code(symbol_root, expiry):
    dt_obj = datetime.strptime(expiry, '%d-%m-%Y')
    formatted_date = dt_obj.strftime('%d %b %Y')
    name = symbol_root + " " + formatted_date
    df = pd.read_csv(
        "ScripMaster.csv")

    df.columns = df.columns.str.strip()
    for index, row in df.iterrows():
        if row['Name'] == name:

            return row['ScripCode']
    return None

callStrike=None
putStrike=None

def get_token(symbol, strike, ScripType,exp):
    df = pd.read_csv("ScripMaster.csv")
    row = df.loc[(df['SymbolRoot'] == symbol)& (df['Expiry'] == exp) & (df['StrikeRate'] == strike) & (df['ScripType'] == ScripType)]
    if not row.empty:
        token = row.iloc[0]['ScripCode']
        return token

def main_strategy():
    global result_dict,callStrike,putStrike,stockdevaccount,client_dict
    ExpieryList = []
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                if params["runonce"]== False:
                    params["runonce"]=True
                    time.sleep(3)
                    parsed_date = datetime.strptime(params['Expiery'], "%d-%b-%y")
                    formatted_date = parsed_date.strftime("%d-%m-%Y")
                    print("formatted_date: ", formatted_date)

                    token = find_scrip_code(symbol_root=params['Symbol'], expiry=formatted_date)
                    Spotltp = int(FivePaisaIntegration.get_ltp(token))
                    last_two_digits = Spotltp % 100

                    if last_two_digits<=15 and last_two_digits>00:
                        callStrike=custom_round(int(Spotltp),"BANKNIFTY")-params['strikeStep']
                        putStrike=custom_round(int(Spotltp),"BANKNIFTY")+params['strikeStep']

                    if last_two_digits > 15 and last_two_digits < 26:
                        last_two_digits = 26

                    if last_two_digits > 75 and last_two_digits < 85:
                        last_two_digits = 74

                    if last_two_digits>15 and last_two_digits<85:
                        callStrike=custom_round(int(Spotltp),"NIFTY")-50
                        putStrike=custom_round(int(Spotltp),"NIFTY")+50



                    if last_two_digits>=85 and last_two_digits<99:
                        callStrike=custom_round(int(Spotltp),"BANKNIFTY")-params['strikeStep']
                        putStrike=custom_round(int(Spotltp),"BANKNIFTY")+params['strikeStep']


                    date_obj = datetime.strptime(params['TradeExp'], "%d-%b-%y")
                    trade_formatted_date_str = date_obj.strftime("%Y-%m-%d")

                    params["CallToken"]= get_token(symbol=params['Symbol'],strike=callStrike,ScripType="CE",exp=trade_formatted_date_str)

                    params["callstrike"]= callStrike
                    params["callSymbol"] = f"{params['Symbol']}_{Stockdeveloper.convert_date(params['TradeExp'])}_CE_{params['callstrike']}"


                    calldata=FivePaisaIntegration.get_historical_data(timframe=params['Timeframe'],
                                                                      token=int(params["CallToken"]),
                                                                      symbol=params['Symbol'])
                    call_high_value = calldata.iloc[-1]['High']
                    call_low_value = calldata.iloc[-1]['Low']
                    if (call_high_value-call_low_value)>params["OptionRange"]:
                        params["TradeDisable"] = False
                        orderlog = (
                            f"{timestamp} Trade will not be taken call high:{call_high_value} call low: {call_low_value}, difference:{ (call_high_value-call_low_value)}, optionrange:{params['OptionRange']}")
                        print(orderlog)
                        write_to_order_logs(orderlog)


                    print("Candletime: ", calldata.iloc[-1]['Datetime'])
                    print("call_high_value: ", call_high_value)
                    print("call_low_value: ", call_low_value)
                    # NIFTY_06-JUN-2024_CE_22700
                    params["PutToken"] =get_token(symbol=params['Symbol'],strike=putStrike,ScripType="PE",exp=trade_formatted_date_str)
                    params["putstrike"]= putStrike
                    params["putSymbol"] = f"{params['Symbol']}_{Stockdeveloper.convert_date(params['TradeExp'])}_PE_{params['putstrike']}"
                    print("putSymbol: ",params["putSymbol"])
                    putdata=FivePaisaIntegration.get_historical_data(timframe=params['Timeframe'],
                                                                      token=int(params["PutToken"]) ,
                                                                      symbol=params['Symbol'])
                    put_high_value = putdata.iloc[-1]['High']
                    put_low_value = putdata.iloc[-1]['Low']
                    if (put_high_value-put_low_value)>params["OptionRange"]:
                        params["TradeDisable"]= False
                        orderlog = (
                            f"{timestamp} Trade will not be taken put high:{put_high_value} putlow: {put_low_value}, difference:{(put_high_value-put_low_value)}, optionrange:{params['OptionRange']}")
                        print(orderlog)
                        write_to_order_logs(orderlog)



                    print("put_high_value: ", put_high_value)
                    print("put_low_value: ", put_low_value)
                    params["CallLow"] = call_low_value-params["SlBufferPts"]
                    params["PutLow"] = put_low_value-params["SlBufferPts"]

                    params["BuyCall"] = call_high_value * params["EntryPercentage"] * 0.01
                    params["BuyCall"] = params["BuyCall"]+call_high_value

                    params["BuyPut"]=put_high_value* params["EntryPercentage"] * 0.01
                    params["BuyPut"]=params["BuyPut"]+put_high_value

                    if params["TradeDisable"]==True:

                        orderlog=(f"{timestamp} Spot ltp = {Spotltp}, nearest atm= {custom_round(int(Spotltp),params['Symbol'])} Buy Price for call {params['callSymbol']}:  {params['BuyCall']}, Buy Price Put {params['putSymbol']}: {params['BuyPut']}, "
                                  f"candletime ={calldata.iloc[-1]['Datetime']}")
                        print(orderlog)
                        write_to_order_logs(orderlog)



            callltp=FivePaisaIntegration.get_ltp(int(params["CallToken"]))
            putltp = FivePaisaIntegration.get_ltp(int(params["PutToken"]))

            print("callltp: ",callltp)
            print("putltp: ",putltp)

            if (
                    putltp>=params["BuyPut"] and
                    params["BuyPut"]>0 and
                    params["Trade"] is None and params["TradeDisable"]==True
            ):
                params["Trade"]="PUT"

                params["Stoploss"]= params["PutLow"]-params["SlBufferPts"]
                params["Target"] = (params["BuyPut"]-params["Stoploss"])+params["BuyPut"]
                print(
                    f"{timestamp} Buy Order executed put side {params['Symbol']}{params['putstrike']} @  {params['BuyPut']},stoploss= {params['Stoploss']}, "
                    f"target= {params['Target']}  ")
                stockdev_multiclient_orderplacement_buy(basesymbol=params['Symbol'],client_dict=client_dict,timestamp=timestamp, symbol=params["putSymbol"],
                                                            direction="BUY", Stoploss=params['Stoploss'], Target=params['Target'],
                                                            qty=params["Quantity"], price=putltp, side="PUT")



            if (
                    callltp>=params["BuyCall"] and
                    params["BuyCall"]>0 and
                    params["Trade"] is None and params["TradeDisable"]==True
            ):
                params["Trade"]="CALL"
                params["Stoploss"] = params["CallLow"]-params["SlBufferPts"]
                params["Target"] = (params["BuyCall"] - params["Stoploss"]) + params["BuyCall"]
                orderlog = (
                    f"{timestamp} Buy Order executed call side {params['Symbol']}{params['callstrike']}@ {params['BuyCall']},stoploss= {params['Stoploss']}, "
                    f"target= {params['Target']}  ")
                print(orderlog)
                stockdev_multiclient_orderplacement_buy(basesymbol=params['Symbol'],client_dict=client_dict,timestamp=timestamp, symbol=params["callSymbol"],
                                                            direction="BUY", Stoploss=params['Stoploss'], Target=params['Target'],
                                                            qty=params["Quantity"], price=callltp,side="CALL"


                                                    )



            if params["Trade"]=="PUT":
                if putltp>=params["Target"] and params["Target"]>0:
                    params["Target"]=0
                    orderlog = (
                        f"{timestamp} put target executed @ {putltp}")
                    print(orderlog)
                    stockdev_multiclient_orderplacement_exit(basesymbol=params['Symbol'],client_dict=client_dict,
                                                                timestamp=timestamp, symbol=params["putSymbol"],
                                                                direction="SELL", Stoploss=params['Stoploss'],
                                                                Target=params['Target'],
                                                                qty=params["Quantity"], price=putltp,log="Target executed PUT trade @ ")
                    params["Trade"] = "NOTRADE"



                if putltp<=params["Stoploss"] and params["Stoploss"]>0:
                    params["Stoploss"]=0
                    orderlog = (
                        f"{timestamp} put Stoploss executed @ {putltp}")
                    print(orderlog)
                    stockdev_multiclient_orderplacement_exit(basesymbol=params['Symbol'],client_dict=client_dict,
                                                                timestamp=timestamp, symbol=params["putSymbol"],
                                                                direction="SELL", Stoploss=params['Stoploss'],
                                                                Target=params['Target'],
                                                                qty=params["Quantity"], price=putltp,log="Stoploss executed PUT trade @ ")
                    params["Trade"] = "NOTRADE"



                if params["Trade"] == "CALL":
                    if callltp >= params["Target"] and params["Target"] > 0:
                        params["Target"] = 0
                        orderlog = (
                            f"{timestamp} call target executed @ {callltp}")
                        print(orderlog)
                        stockdev_multiclient_orderplacement_exit(basesymbol=params['Symbol'],client_dict=client_dict,
                                                                    timestamp=timestamp, symbol=params["callSymbol"],
                                                                    direction="SELL", Stoploss=params['Stoploss'],
                                                                    Target=params['Target'],
                                                                    qty=params["Quantity"], price=callltp,log="Target executed CALL trade @ ")
                        params["Trade"] = "NOTRADE"


                    if callltp <= params["Stoploss"] and params["Stoploss"] > 0:
                        params["Stoploss"] = 0
                        orderlog = (
                            f"{timestamp} call Stoploss executed @ {callltp}")
                        print(orderlog)
                        stockdev_multiclient_orderplacement_exit(basesymbol=params['Symbol'],client_dict=client_dict,
                                                                    timestamp=timestamp, symbol=params["callSymbol"],
                                                                    direction="SELL", Stoploss=params['Stoploss'],
                                                                    Target=params['Target'],
                                                                    qty=params["Quantity"], price=callltp,log="Stoploss executed CALL trade @ ")
                        params["Trade"] = "NOTRADE"


    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()

def TimeBasedExit():
    global result_dict, callStrike, putStrike, stockdevaccount, client_dict
    ExpieryList = []
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                callltp = FivePaisaIntegration.get_ltp(int(params["CallToken"]))
                putltp = FivePaisaIntegration.get_ltp(int(params["PutToken"]))
                if params["Trade"] == "PUT"  :
                    stockdev_multiclient_orderplacement_exit(basesymbol=params['Symbol'], client_dict=client_dict,
                                                             timestamp=timestamp, symbol=params["putSymbol"],
                                                             direction="SELL", Stoploss=params['Stoploss'],
                                                             Target=params['Target'],
                                                             qty=params["Quantity"], price=putltp,
                                                             log="Target executed PUT trade @ ")
                if params["Trade"] == "CALL":
                    stockdev_multiclient_orderplacement_exit(basesymbol=params['Symbol'], client_dict=client_dict,
                                                            timestamp=timestamp, symbol=params["callSymbol"],
                                                            direction="SELL", Stoploss=params['Stoploss'],
                                                            Target=params['Target'],
                                                            qty=params["Quantity"], price=callltp,
                                                            log="Stoploss executed CALL trade @ ")

                if params["Trade"] == "NOTRADE":
                    orderlog = (
                        f"{timestamp} No position active Nothing to exit @ {symbol_value}")
                    print(orderlog)
                    write_to_order_logs(orderlog)
                    params["Trade"]="CCCC"



    except Exception as e:
        print("Error happened in Time based exit loop: ", str(e))
        traceback.print_exc()




FivePaisaIntegration.login()
while True:
    StartTime = credentials_dict.get('StartTime')
    Stoptime = credentials_dict.get('Stoptime')
    start_time = datetime.strptime(StartTime, '%H:%M').time()
    stop_time = datetime.strptime(Stoptime, '%H:%M').time()

    now = datetime.now().time()
    if now >= start_time and now < stop_time:
        main_strategy()
        time.sleep(1)

    if now ==stop_time:
        TimeBasedExit()







        # eogkopj