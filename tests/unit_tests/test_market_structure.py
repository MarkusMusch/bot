from datetime import datetime
import pandas as pd

from src.Assets import btc_cont
from src.MarketStructure import MarketStructure


def test_ms_load_data():
    """Test if data is being loaded correctly."""


    test_df = pd.DataFrame([58348.6, 58224.3, 57796.9, 57430.2],
                           columns=['open'])

    df = pd.read_csv('./database/datasets/binance_futures/BTCBUSD/1h.csv')
    df = df[(df['open time'] >= 1613934000000)
            & (df['open time'] <= 1613944800000)]

    df.reset_index(inplace=True)

    assert df['open'].equals(test_df['open'])
                 

def test_ms_stay_in_range():
    """Test if market structure staying in range is being reconginzed
    correctly."""

    ms = MarketStructure(btc_cont.ath, btc_cont.prev_low, btc_cont.ath,
                         btc_cont.prev_low)

    df = pd.read_csv('./database/datasets/binance_futures/BTCBUSD/1h.csv')
    df = df[(df['open time'] >= 1613934000000)
            & (df['open time'] <= 1613959200000)]

    for idx, row in df.iterrows():
        ms.next_candle(row)

    assert ms.msb is False
    assert ms.stay_in_range is True
    assert ms.continuation is False
    assert ms.trend is False

    assert ms.prev_high[0] == 57743.1
    assert ms.prev_low[0] == 56312.5
    assert ms.provisional_high[0] == 57388.0
    assert ms.provisional_low[0] == 56312.5


def test_ms_continuation():
    """Test if market structure trend continuation is being reconginzed
    correctly."""

    ms = MarketStructure(btc_cont.ath, btc_cont.prev_low, btc_cont.ath,
                         btc_cont.prev_low)

    df = pd.read_csv('./database/datasets/binance_futures/BTCBUSD/1h.csv')
    df = df[(df['open time'] >= 1613934000000)
            & (df['open time'] <= 1613962800000)]

    for idx, row in df.iterrows():
        ms.next_candle(row)

    assert ms.msb is False
    assert ms.stay_in_range is False
    assert ms.continuation is True
    assert ms.trend is False

    assert ms.prev_high[0] == 57388.0
    assert ms.prev_low[0] == 55888.2
    assert ms.provisional_high[0] == 57388.0
    assert ms.provisional_low[0] == 55888.2


def test_ms_break():
    """Test if market structure break is being reconginzed correctly."""

    ms = MarketStructure(btc_cont.ath, btc_cont.prev_low, btc_cont.ath,
                         btc_cont.prev_low)

    df = pd.read_csv('./database/datasets/binance_futures/BTCBUSD/1h.csv')
    df = df[(df['open time'] >= 1613934000000)
            & (df['open time'] <= 1614081600000)]

    for idx, row in df.iterrows():
        ms.next_candle(row)

    assert ms.msb is True
    assert ms.stay_in_range is False
    assert ms.continuation is False
    assert ms.trend is True

    assert ms.prev_high[0] == 49584.5
    assert ms.prev_low[0] == 45000.1
    assert ms.provisional_high[0] == 49584.5
    assert ms.provisional_low[0] == 45000.1


def test_ms():
    """Test if market structure is being reconginzed correctly
    over a longer period."""

    ms = MarketStructure(btc_cont.ath, btc_cont.prev_low, btc_cont.ath,
                         btc_cont.prev_low)

    df = pd.read_csv('./database/datasets/binance_futures/BTCBUSD/1h.csv')
    df = df[(df['open time'] >= 1613934000000)
            & (df['open time'] <= 1616338800000)]

    for idx, row in df.iterrows():
        ms.next_candle(row)

    assert ms.msb is False
    assert ms.stay_in_range is True
    assert ms.continuation is False
    assert ms.trend is False

    assert ms.prev_high[0] == 57410.4
    assert ms.prev_low[0] == 55478.9
    assert ms.provisional_high[0] == 57642.1
    assert ms.provisional_low[0] == 55945.5
