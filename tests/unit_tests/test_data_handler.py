from datetime import datetime

import pandas as pd

from src.RESTClient import BinanceFuturesClient
from src.DataHandler import DataHandler


def test_data_fetch_historical():
    """Request historical data from Binance API."""

    test_df = pd.DataFrame([58348.6, 58224.3, 57796.9, 57430.2],
                           columns=['open'])

    ec = BinanceFuturesClient()
    dh = DataHandler(vd=False)

    df = dh.fetch_historical_data(ec, 'BTCBUSD', '1h',
                                  datetime(2021, 2, 21, 20, 0, 0, 0),
                                  datetime(2021, 2, 21, 23, 0, 0, 0))

    assert df['open'].equals(test_df['open'])


def test_data_fetch_current():
    """Request current data from Binance API."""

    ec = BinanceFuturesClient()
    dh = DataHandler(vd=False,)

    df = dh.fetch_current_data(ec, 'BTCBUSD', '1h')

    assert len(df.columns) != 0
