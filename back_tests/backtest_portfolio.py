import logging
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from src.RESTClient import BinanceFuturesClient
from src.Assets import btc_cont, eth_cont, sol_cont, doge_cont
from src.DataHandler import DataHandler
from src.Portfolio import Portfolio
from src.Stats import Stats


def initialize_portfolio(live: bool = False):
    logging.basicConfig(filename='scalp_bot.log', level=logging.WARNING)

    ec = BinanceFuturesClient()

    stats = Stats()
    dh = DataHandler(vd=False)

    logging.getLogger().setLevel(logging.WARNING)

    markets = [btc_cont, eth_cont, sol_cont, doge_cont]

    portfolio = Portfolio(ec, dh, markets, live=live)

    portfolio.build_portfolio()

    portfolio.initialize_trades()

    portfolio.plot_equity()

    stats.get_stats(portfolio.equity_curve)
    stats.plot_returns(portfolio.equity_curve)

    logging.getLogger().setLevel(logging.INFO)

    logging.info("INITIALIZATION DONE!")

    return portfolio


def execute(portfolio):
    portfolio.live_trades()


if __name__ == '__main__':

    portfolio = initialize_portfolio(live=False)
