import os
import sys

from back_tests.Backtest import Backtest
from src.Assets import btc_rev  # , eth_rev, bnb_rev
from src.RESTClient import BinanceFuturesClient
from src.strategies.ReversalTrade import ReversalTradeRSI

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


if __name__ == '__main__':

    ec = BinanceFuturesClient()

    bt = Backtest()

    markets = [btc_rev]  # , eth_rev, bnb_rev]

    risk_samples = [0.05]  # [0.001, 0.005, 0.01, 0.05, 0.1, 0.2]
    leverage_samples = [3]  # [1, 3, 5, 10]
    risk_reward = [2.0, 3.0]

    num_rr_ratios = len(risk_reward)
    num_risk_samples = len(risk_samples)
    num_lev_samples = len(leverage_samples)

    bt.run(ec, ReversalTradeRSI, markets, risk_samples, leverage_samples,
           risk_reward)

    print('DONE!')
