import os
import sys

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.RESTClient import BinanceFuturesClient
from src.DataHandler import DataHandler

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


def download(markets: list):

    ec = BinanceFuturesClient()
    dh = DataHandler(vd=False)

    for market in markets:
        df = dh.aggregate_data(ec, market, '1h',
                               datetime(2017, 7, 14, 0, 0, 0, 0))

        df.to_csv('./database/' + market + '_1h.csv')


def compute_vds():
    markets = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'DOGEUSDT']

    for market in markets:

        df = pd.read_csv(market + '_1h.csv')
        dh = DataHandler(vd=False)

        df = dh._compute_vd(df)
        df = dh._compute_vd_ma(df, 2400)
        df = dh._compute_cvd(df)

        df.to_csv(market + '_1h.csv')


def plot_vdma():
    markets = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'DOGEUSDT']

    for market in markets:
        df = pd.read_csv(market + '_1h.csv')

        fig, ax = plt.subplots()

        df['datetime'] = pd.to_datetime(df['open time'], unit='ms')

        ax.plot(np.array(df['datetime']), np.array(df['close']), color='red')
        ax2 = ax.twinx()
        ax2.plot(np.array(df['datetime']),
                 np.array(df['volume_delta_moving_average_base_asset']))
        plt.show()


def plot_cvd():
    markets = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'DOGEUSDT']

    for market in markets:

        df = pd.read_csv(market + '_1h_spot.csv')

        fig, ax = plt.subplots()

        df['datetime'] = pd.to_datetime(df['open time'], unit='ms')

        ax.plot(np.array(df['datetime']), np.array(df['close']), color='red')
        ax2 = ax.twinx()
        ax2.plot(np.array(df['datetime']), np.array(df['cvd_quote_asset']))
        plt.show()


usdt_markets = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'DOGEUSDT']
busd_markets = ['BTCBUSD', 'ETHBUSD', 'BNBBUSD', 'SOLBUSD', 'DOGEBUSD']
download(busd_markets)
# compute_vds()
# plot_vdma()
# plot_cvd()
