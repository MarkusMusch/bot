import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from back_tests.Backtest import Backtest
from src.RESTClient import BinanceFuturesClient
from src.Assets import btc_cont, eth_cont, sol_cont, doge_cont, Timeframes
from src.strategies.ContinuationTrade import ContinuationTrade
from src.Stats import Stats


if __name__ == '__main__':

    ec = BinanceFuturesClient()
    bt = Backtest()
    stats = Stats()
    bt = Backtest()

    markets = [btc_cont, eth_cont, sol_cont, doge_cont]

    risk_samples = [0.001, 0.005, 0.01, 0.05, 0.1, 0.2]
    leverage_samples = [1, 3, 5, 10]
    risk_reward = [2.0, 3.0]

    for market in markets:
        bt.run(ec, ContinuationTrade, market, risk_samples, leverage_samples,
               risk_reward, Timeframes)

    print('DONE!')
