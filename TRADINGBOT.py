import ccxt
import numpy as np
from threading import Thread, Lock
#these are fake api credential, if you want to use the bot insert yours but DO NOT share them with ANYBODY
api_secret='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
api_password='xxxxxxxxxxx'
api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

lock= Lock()

exchange = ccxt.coinbasepro({
    
    'enableRateLimit': True,
    'apiKey': api_key,
    'secret': api_secret,
    'password': api_password,
})
#get current price of BTC
ticker = exchange.fetch_ticker('BTC/USD')
price = float(ticker['last'])

#will calculate the avg up until the end of the interval
def get_avg_price(interval):
    ohlcv = exchange.fetch_ohlcv('BTC/USD', '1d', limit=interval) #ohlcv stands for "Open, High, Low, Close, Volume", to calculate the 
    closes = [x[4] for x in ohlcv]                                #avg we are only interested in the close price(fetch_ohlcv returns list of lists)
    return np.mean(closes)
#uses the func above to update the average 
def update_avg(interval, variable):
    avg_price = get_avg_price(interval)
    with lock:
        variable.value = avg_price


# Calculate the 30 ad 60 day average price
t1 = Thread(target= update_avg(30, float(average_30d)))
t1.start()
t2 = Thread(target=update_avg(60, float(average_60d)))
t2.start()

#Wait for them to join 
t1.join()
t2.join()

#Buy or sell the BTC
amount =100000/price
if price > average_30d and price > average_60d:
    order = exchange.create_market_buy_order('BTC/USD', amount)
elif price < average_30d and price < average_60d:
    order = exchange.create_market_sell_order('BTC/USD', amount)
print(order)
