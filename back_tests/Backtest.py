from datetime import datetime
import os
from enum import Enum

import ta
import pandas as pd
import matplotlib.pyplot as plt

from src.Assets import Asset
from src.MarketStructure import MarketStructure
from src.RESTClient import RESTClient
from src.Stats import Stats
from src.Strategy import Strategy


class Backtest():
    """Backtests a trading strategy on historical data."""

    def __init__(self):
        pass

    def backtest(self, strat: Strategy, timeframe: str, market_name: str,
                 start: datetime):
        """Goes through a given set of historical data and applies the trading
        strategy to this data."""

        df = pd.read_csv('./database/datasets/binance_futures/' +
                         market_name + '/' + timeframe + '.csv')
        df = df[df['open time'] >= int(start.timestamp()*1000)]

        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()

        for index, row in df.iterrows():
            strat.next_candle_live(row)

    def run(self, ec: RESTClient, trade: Strategy, market: Asset,
            risk_samples: list, leverage_samples: list,
            risk_reward: list, timeframes: Enum) -> None:
        """Runs the backtest for a given set of markets."""

        stats = Stats()
        num_rr_ratios = len(risk_reward)
        num_risk_samples = len(risk_samples)
        num_lev_samples = len(leverage_samples)
        market_name = market.market_name
        ath = market.ath
        prev_low = market.prev_low
        start = market.start_time

        for timeframe in timeframes:

            fig, axs = plt.subplots(num_risk_samples*num_lev_samples
                                    * num_rr_ratios, 2,
                                    figsize=(15, 5 * num_risk_samples
                                             * num_lev_samples
                                             * num_rr_ratios))
            fig.suptitle('Equity Curves and Position Sizes of Backtests for '
                         + 'Market Structure Break Strategy')

            for idxr, risk in enumerate(risk_samples):

                for idxl, leverage in enumerate(leverage_samples):

                    for idxrr, rr in enumerate(risk_reward):

                        market.timeframe = timeframe.value
                        market.max_risk = risk
                        market.max_leverage = leverage
                        market.risk_reward = rr

                        ms = MarketStructure(ath, prev_low, ath, prev_low)
                        rtit = trade(ec, ms, market)

                        self.backtest(rtit, timeframe.value, market_name,
                                      start)

                        stats_dict = stats.get_stats(rtit.equity_curve)

                        idx_subplot = + num_lev_samples*num_rr_ratios*idxr \
                            + num_rr_ratios*idxl + idxrr

                        axs[idx_subplot][0].plot(rtit.equity_curve)
                        axs[idx_subplot][0].set_title(
                            'Equity Curve ' + market_name
                            + ' at max. risk {:.2%} '.format(risk)
                            + 'with max. leverage {:.1f} '.format(leverage)
                            + 'and R/R {:.1f} \n'.format(rr)
                            + 'Sharpe: {:.2f}, '.format(stats_dict['sharpe'])
                            + 'Sortino: {:.2f}, '.format(stats_dict['sortino'])
                            + 'Max. '
                            + 'Drawdown: {:.2%}'.format(stats_dict['max_dd']))
                        axs[idx_subplot][0].grid(True)

                        axs[idx_subplot][1].plot(rtit.position_size)
                        axs[idx_subplot][1].set_title(
                            'Position Size ' + market_name + ', max. risk '
                            + str(risk) + ', max. leverage '
                            + str(leverage) + ', R/R ' + str(rr))
                        axs[idx_subplot][1].grid(True)

            path = './back_tests/backtest_reports/' + market.strategy_name \
                   + '/' + market_name + '/'
            if not os.path.exists(path):
                os.makedirs(path)

            plt.savefig(path + timeframe.value + '.pdf', dpi=75)
        print(market_name, ' done! \n')
