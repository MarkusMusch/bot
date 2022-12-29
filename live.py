import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from src.RESTClient import BinanceFuturesClient
from src.Assets import btc_cont_live, eth_cont_live, sol_cont_live, \
                       doge_cont_live
from src.DataHandler import DataHandler
from src.Portfolio import Portfolio


def initialize_portfolio(markets: list, live: bool = False) -> Portfolio:
    logging.basicConfig(filename='scalp_bot.log', level=logging.WARNING)

    ec = BinanceFuturesClient()
    ec.read_config()

    dh = DataHandler(vd=False)

    logging.getLogger().setLevel(logging.WARNING)

    portfolio = Portfolio(ec, dh, markets, live=live)

    portfolio.build_portfolio()

    portfolio.initialize_trades()

    logging.getLogger().setLevel(logging.INFO)

    logging.info("INITIALIZATION DONE!")

    return portfolio


def execute(portfolio):
    portfolio.live_trades()


def trade(portfolio):
    sched = BlockingScheduler()
    sched.add_job(execute, 'cron', [portfolio], hour='0-23')
    sched.start()


if __name__ == '__main__':

    markets = [btc_cont_live, eth_cont_live, sol_cont_live, doge_cont_live]

    portfolio = initialize_portfolio(markets, live=True)

    trade(portfolio)
