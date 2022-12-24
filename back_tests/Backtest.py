from datetime import datetime

import ta
import pandas as pd
import matplotlib.pyplot as plt

from src.RESTClient import RESTClient
from src.Stats import Stats
from src.MarketStructure import MarketStructure
from src.Strategy import Strategy


class Backtest():
    """Backtests a trading strategy on historical data."""

    def __init__(self):
        pass

    def backtest(self, strat: Strategy, timeframe: str, market_name: str,
                 start: datetime):
        """Goes through a given set of historical data and applies the trading
        strategy to this data."""

        df = pd.read_csv('./database/' + market_name + '_' + timeframe
                         + '.csv')
        df = df[df['open time'] >= int(start.timestamp()*1000)]

        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()

        for index, row in df.iterrows():
            strat.next_candle_live(row)

    def run(self, ec: RESTClient, trade: Strategy, markets: list,
            risk_samples: list, leverage_samples: list,
            risk_reward: list) -> None:
        """Runs the backtest for a given set of markets."""

        stats = Stats()

        num_rr_ratios = len(risk_reward)
        num_risk_samples = len(risk_samples)
        num_lev_samples = len(leverage_samples)

        for idxm, market in enumerate(markets):

            market_name = market.market_name
            ath = market.ath
            prev_low = market.prev_low
            start = market.start_time
            initial_equity = market.initial_equity
            timeframe = market.timeframe

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

                        ms = MarketStructure(ath, prev_low, ath, prev_low)
                        rtit = trade(ec, ms, 'Reversal Trade', market,
                                     market_name, initial_equity, risk,
                                     leverage, risk_reward=rr)

                        self.backtest(rtit, timeframe, market_name, start)

                        idx_subplot = + num_lev_samples*num_rr_ratios*idxr \
                            + num_rr_ratios*idxl + idxrr

                        axs[idx_subplot][0].plot(rtit.equity_curve)
                        axs[idx_subplot][0].set_title(
                            'Equity Curve ' + market_name + ' at max. risk '
                            + str(risk) + ' with max. leverage '
                            + str(leverage) + ' and R/R ' + str(rr))
                        axs[idx_subplot][0].grid(True)
                        axs[idx_subplot][1].plot(rtit.position_size)
                        axs[idx_subplot][1].set_title(
                            'Position Size ' + market_name + ', max. risk '
                            + str(risk) + ', max. leverage '
                            + str(leverage) + ', R/R ' + str(rr))
                        axs[idx_subplot][1].grid(True)

                        stats.get_stats(rtit.equity_curve)

            plt.savefig('./back_tests/backtest_reports/'
                        + market.strategy_name + '_' + market_name + '.pdf',
                        dpi=75)
            print(market_name, ' done! \n')
            ms.structure
