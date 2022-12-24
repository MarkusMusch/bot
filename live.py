import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from src.RESTClient import BinanceFuturesClient
from src.DataHandler import DataHandler
from src.Portfolio import Portfolio
from src.Assets import btc_cont_live, eth_cont_live, sol_cont_live, \
                       doge_cont_live, btc_rev_live, eth_rev_live, \
                       bnb_rev_live


def initialize_portfolio(live: bool = False):
    logging.basicConfig(filename='scalp_bot.log', level=logging.WARNING)

    ec = BinanceFuturesClient()
    ec.read_config()

    dh = DataHandler(vd=False)

    logging.getLogger().setLevel(logging.WARNING)

    markets = [btc_cont_live, eth_cont_live, sol_cont_live, doge_cont_live,
               btc_rev_live, eth_rev_live, bnb_rev_live]

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

    live = True

    portfolio = initialize_portfolio(live=live)

    if live:
        trade(portfolio)
