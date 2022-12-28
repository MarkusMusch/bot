"""Implement classes to manage a portfolio of strategies.

Classes
----------
    Portfolio:
        Represents a portfolio of trading strategies.
"""

from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from src.DataHandler import DataHandler
from src.MarketStructure import MarketStructure
from src.RESTClient import RESTClient
from src.Strategy import Strategy


class Portfolio:
    """Collect several trading strategies into a portfolio of trading
    strategies.

    ...

    Attributes
    ----------
    strategies : list
        List of trading strategies.
    markets : dict
        Dictionary of tickers and their corresponding markets.
    _dh : DataHandler
        DataHandler object to fetch data.
    _ec : RESTClient
        RESTClient object to fetch data.
    _live : bool
        Whether the portfolio is live or not.

    Methods
    -------
    equity_curve() -> float:
        Returns the current equity curve of the portfolio.
    plot_equity() -> None:
        Plot the portfolios equity curve
    add_strategy(strategy: Strategy) -> None:
        Add a new strategy to the portfolio.
    build_portfolio() -> None:
        Build a portfolio of strategies from given markets
    """

    def __init__(self, ec: RESTClient, dh: DataHandler, markets: dict,
                 strategies: list = [], live: bool = False):
        """
        Parameters
        ----------
        ec : RESTClient
            RESTClient object to fetch data.
        dh : DataHandler
            DataHandler object to fetch data.
        markets : dict
            Dictionary of tickers and their corresponding markets.
        strategies : list
            List of trading strategies.
        live : bool
            Whether the portfolio is live or not.
        """

        self.strategies = strategies
        self.markets = markets
        self._dh = dh
        self._ec = ec
        self._live = live

    @property
    def equity_curve(self) -> float:
        """Returns the current equity curve of the portfolio.

        Returns
        -------
        float
            The current equity curve of the portfolio.
        """

        for idx, strat in enumerate(self.strategies):
            if idx == 0:
                pf = strat[1].equity_curve
            else:
                asset = strat[1].equity_curve
                size_diff = pf.size - asset.size
                if size_diff > 0:
                    asset = np.concatenate((np.full(size_diff, asset[0]),
                                            asset))
                elif size_diff < 0:
                    pf = np.concatenate((np.full(size_diff, pf[0]), pf))
                pf = np.add(pf, asset)

        pf = (1./len(self.strategies))*pf

        return pf

    def plot_equity(self) -> None:
        """Plot the portfolios equity curve."""

        pf = self.equity_curve

        plt.figure(figsize=(18, 9))
        plt.grid(True)
        plt.plot(pf)
        plt.show()

    def add_strategy(self, strategy: Strategy) -> None:
        """Add a new strategy to the portfolio.

        Parameters
        ----------
        strategy : Strategy
            Strategy to add to the portfolio.
        """

        self.strategies.append(strategy)

    def build_portfolio(self) -> None:
        """Build a portfolio of strategies from given markets"""

        for idxm, market in enumerate(self.markets):

            strategy_constructor = market.strategy
            ath = market.ath
            prev_low = market.prev_low

            ms = MarketStructure(ath, prev_low, ath, prev_low)

            strategy = strategy_constructor(self._ec, ms, market,
                                            live=self._live)

            self.add_strategy((market, strategy))

    def initialize_trades(self) -> None:
        """Go through a given set of historical data and applies the trading
        strategy to this data, tracking results."""

        for idx, strat in enumerate(tqdm(self.strategies)):
            start_time = strat[0].start_time
            end_time = start_time + timedelta(days=40)

            while start_time < datetime.now():

                df = self._dh.fetch_historical_data(self._ec,
                                                    strat[0].market_name,
                                                    strat[1].timeframe,
                                                    start_time, end_time)

                if self._live:
                    for index, row in df.iterrows():
                        strat[1].next_candle_init(row)
                else:
                    for index, row in df.iterrows():
                        strat[1].next_candle_live(row)

                start_time = end_time
                end_time = end_time + timedelta(days=40)

    def live_trades(self) -> None:
        """Get the newest market data and applies the trading strategy to this
        data, executing trades."""

        for idx, strat in enumerate(tqdm(self.strategies)):

            market_name = strat[0].market_name

            df = self._dh.fetch_current_data(self._ec, market_name,
                                             strat[1].timeframe.value)

            strat[1].next_candle_live(df.iloc[-1])
