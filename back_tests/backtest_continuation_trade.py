import os
import sys

from back_tests.Backtest import Backtest
from src.Assets import btc_cont  # , eth_cont, sol_cont, doge_cont
from src.Stats import Stats
from src.RESTClient import BinanceFuturesClient
from src.strategies.ContinuationTrade import ContinuationTrade

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


if __name__ == '__main__':

    ec = BinanceFuturesClient()

    bt = Backtest()

    markets = [btc_cont]  # , eth_cont, sol_cont, doge_cont]

    stats = Stats()
    bt = Backtest()

    risk_samples = [0.001, 0.005]  # , 0.01, 0.05, 0.1, 0.2]
    leverage_samples = [1]  # , 3, 5, 10]
    risk_reward = [2.0]  # , 3.0]

    num_rr_ratios = len(risk_reward)
    num_risk_samples = len(risk_samples)
    num_lev_samples = len(leverage_samples)

    bt.run(ec, ContinuationTrade, markets, risk_samples, leverage_samples,
           risk_reward)

    print('DONE!')
