import os
import sys

from datetime import datetime, timedelta

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from src.RESTClient import BinanceFuturesClient
from src.DataHandler import DataHandler
from src.Assets import Timeframes


def download(market: str, timeframe: str, delta: timedelta):

    ec = BinanceFuturesClient()
    dh = DataHandler(vd=False)

    df = dh.aggregate_data(ec, market, timeframe,
                           datetime(2017, 7, 14, 0, 0, 0, 0),
                           delta)

    path = './database/datasets/binance_futures/' + market + '/'
    if not os.path.exists(path):
        os.makedirs(path)

    df.to_csv(path + timeframe + '.csv')


busd_markets = ['BTCBUSD', 'ETHBUSD', 'SOLBUSD', 'DOGEBUSD']

for market in busd_markets:
    download(market, Timeframes.ONE_DAY.value, timedelta(days=999))
    print(Timeframes.ONE_DAY.value + ' done! \n')
    download(market, Timeframes.FOUR_HOURS.value, timedelta(hours=3999))
    print(Timeframes.FOUR_HOURS.value + ' done! \n')
    download(market, Timeframes.ONE_HOUR.value, timedelta(hours=999))
    print(Timeframes.ONE_HOUR.value + ' done! \n')

    print(market + ' done! \n')
