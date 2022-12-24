"""Implement an implementation of Strategy for a msb reversal trade.

Classes
----------
    ReversalTrade:
        Implement the buy and sell logic of a msb reversal trade.
"""

import logging

import pandas as pd
import numpy as np

from src.MarketStructure import MarketStructure
from src.RESTClient import RESTClient
from src.Strategy import Strategy


class ReversalTrade(Strategy):
    """Implements the logical rules for a trend reversal trade triggered by an
    initial market structure break.

    ...

    Methods
    -------
    next_candle_init(row: pd.Series) -> None:
        Initializes the strategy by iterating through historical data without
        executing trades.
    next_candle_live(row: pd.Series) -> None:
        Checks for valid trade set ups with new live data and execute live
        trades.
    """

    def __init__(self, ec: RESTClient, ms: MarketStructure, strat_name: str,
                 asset: dict, market_name: str, equity: float,
                 max_risk: float, max_leverage: float = 1.0,
                 timeframe: str = '1h', live: bool = False,
                 risk_reward: float = 2.0):
        """
        Parameters
        ----------
        ec : RESTClient
            Exchange client to interact with the exchange.
        ms : MarketStructure
            Represent the market structure of the asset.
        strat_name : str
            Name of the strategy.
        asset : dict
            Asset to trade.
        market_name : str
            Ticker of the market to trade.
        equity : float
            Initial equity of the strategy.
        max_risk : float
            Maximum risk per trade.
        max_leverage : float, optional
            Maximum leverage of the strategy, by default 1.0
        timeframe : str, optional
            Timeframe of the strategy, by default '1h'
        live : bool, optional
            Whether the strategy is live or not, by default False
        risk_reward : float, optional
            Minimum risk reward ratio for a trade, by default 2.0
        """

        super().__init__(ec, ms, strat_name, asset, market_name, equity,
                         max_risk, max_leverage, timeframe, live)
        self._risk_reward = risk_reward

    def next_candle_init(self, row: pd.Series) -> None:
        """Initializes the strategy by iterating through historical data
        without executing trades.

        Parameters
        ----------
        row : pd.Series
            Row of the dataframe containing the candle data.
        """

        self._setup_trade(row)

    def next_candle_live(self, row: pd.Series) -> None:
        """Checks for valid trade set ups with new live data and execute live
        trades.

        Parameters
        ----------
        row : pd.Series
            Row of the dataframe containing the candle data.
        """

        self._execute_trade(row)
        self._setup_trade(row)

    def _entry_long(self, row: pd.Series) -> None:
        """Looking for an entry to a long trade after a signal has been
        triggered.

        Parameters
        ----------
        row : pd.Series
            Row of the dataframe containing the candle data.
        """

        price = row['close']
        if price <= self.ms.prev_low[0]:
            self._long_trigger = False
        elif price >= self.ms.prev_high[0] and not self.ms.continuation:
            self._long_trigger = False
        else:
            if price <= self._entry:
                risk = price - self._stop_loss
                reward_risk = (self.ms.prev_high[0] - price)/risk
                if reward_risk >= self._risk_reward:
                    self._target = self.ms.prev_high[0]
                    self._long(price, risk/price)
                    self.num_trades += 1
                    self._long_position = True
                    self._long_trigger = False

    def _exit_long(self, row: pd.Series) -> None:
        """Checks if an open long trade has to be closed.

        Parameters
        ----------
        row : pd.Series
            Row of the dataframe containing the candle data.
        """

        price = row['close']
        if price > self._target:
            self._close_long_trade(price)
            logging.info('Take Profit on Long Position')
            self._long_position = False
            self.wins += 1
            self.win_rate = self.wins/self.num_trades
        if price < self._stop_loss:
            self._close_long_trade(price)
            logging.info('Stop Loss Hit on Long Position')
            self._long_position = False

    def _entry_short(self, row: pd.Series) -> None:
        """Looking for an entry to a short trade after a signal has been
        triggered.

        Parameters
        ----------
        row : pd.Series
            Row of the dataframe containing the candle data.
        """

        price = row['close']
        if price >= self.ms.prev_high[0]:
            self._short_trigger = False
        elif price <= self.ms.prev_low[0] and not self.ms.continuation:
            self._long_trigger = False
        else:
            if price >= self._entry:
                risk = self._stop_loss - price
                reward_risk = (price-self.ms.prev_low[0])/risk
                if reward_risk >= self._risk_reward:
                    self._target = self.ms.prev_low[0]
                    self._short(price, risk/price)
                    self.num_trades += 1
                    self._short_position = True
                    self._short_trigger = False

    def _exit_short(self, row: pd.Series) -> None:
        """Checks if an open short trade has to be closed.

        Parameters
        ----------
        row : pd.Series
            Row of the dataframe containing the candle data.
        """

        price = row['close']
        if price < self._target:
            self._close_short_trade(price)
            logging.info('Take Profit on Short Position')
            self._short_position = False
            self.wins += 1
            self.win_rate = self.wins/self.num_trades
        if price > self._stop_loss:
            self._close_short_trade(price)
            logging.info('Stop Loss Hit on Short Position')
            self._short_position = False

    def _setup_trade(self, row: pd.Series) -> None:
        """Activates trade triggers and sets stop losses.

        Parameters
        ----------
        row : pd.Series
            Row of the dataframe containing the candle data.
        """

        trend, msb, continuation, stay_in_range = self.ms.next_candle(row)
        self.close = row['close']

        if msb and (not trend):
            self._entry = self.ms.prev_high[0]
            self._stop_loss = self.ms.provisional_low[0]
            self._long_trigger = True
        elif msb and trend:
            self._entry = self.ms.prev_low[0]
            self._stop_loss = self.ms.provisional_high[0]
            self._short_trigger = True

        if not self._live:
            self.position_size.append(self._position)
            self.equity_curve = np.append(self.equity_curve, self.equity)

    def _execute_trade(self, row: pd.Series) -> None:
        """Enters trade after triggered and follows through until trade exit.

        Parameters
        ----------
        row : pd.Series
            Row of the dataframe containing the candle data.
        """

        if self._long_trigger:
            self._entry_long(row)
        if self._long_position:
            self._exit_long(row)
        if self._short_trigger:
            self._entry_short(row)
        if self._short_position:
            self._exit_short(row)


class ReversalTradeRSI(ReversalTrade):
    """Implements the logical rules for a trend reversal trade triggered by an
    initial market structure break plus confluence from RSI."""

    def __init__(self, ec: RESTClient, ms: MarketStructure, strat_name: str,
                 asset: dict, market_name: str, equity: float,
                 max_risk: float, max_leverage: float = 1.0,
                 timeframe: str = '1h', live: bool = False,
                 risk_reward: float = 2.0):
        """
        Parameters
        ----------
        ec : RESTClient
            Exchange client to interact with the exchange.
        ms : MarketStructure
            Represent the market structure of the asset.
        strat_name : str
            Name of the strategy.
        asset : dict
            Dictionary containing the asset information.
        market_name : str
            Name of the market.
        equity : float
            Initial equity.
        max_risk : float
            Maximum risk per trade.
        max_leverage : float, optional
            Maximum leverage to use, by default 1.0
        timeframe : str, optional
            Timeframe of the data, by default '1h'
        live : bool, optional
            Whether the strategy is live or not, by default False
        risk_reward : float, optional
            Minimum risk reward ratio, by default 2.0
        """

        super().__init__(ec, ms, strat_name, asset, market_name, equity,
                         max_risk, max_leverage, timeframe, live,
                         risk_reward)

    def _entry_long(self, row: pd.Series) -> None:
        """Looking for an entry to a long trade after a signal has been
        triggered.

        Parameters
        ----------
        row : pd.Series
            Row of the dataframe containing the candle data.
        """

        price = row['close']
        if price <= self.ms.prev_low[0]:
            self._long_trigger = False
        elif price >= self.ms.prev_high[0] and not self.ms.continuation:
            self._long_trigger = False
        else:
            if price <= self._entry and row['rsi'] <= 30:
                risk = price - self._stop_loss
                reward_risk = (self.ms.prev_high[0] - price)/risk
                if reward_risk >= self._risk_reward:
                    self._target = self.ms.prev_high[0]
                    self._long(price, risk/price)
                    self.num_trades += 1
                    self._long_position = True
                    self._long_trigger = False

    def _entry_short(self, row: pd.Series) -> None:
        """Looking for an entry to a short trade after a signal has been
        triggered.

        Parameters
        ----------
        row : pd.Series
            Row of the dataframe containing the candle data.
        """

        price = row['close']
        if price >= self.ms.prev_high[0]:
            self._short_trigger = False
        elif price <= self.ms.prev_low[0] and not self.ms.continuation:
            self._long_trigger = False
        else:
            if price >= self._entry and row['rsi'] >= 70:
                risk = self._stop_loss - price
                reward_risk = (price-self.ms.prev_low[0])/risk
                if reward_risk >= self._risk_reward:
                    self._target = self.ms.prev_low[0]
                    self._short(price, risk/price)
                    self.num_trades += 1
                    self._short_position = True
                    self._short_trigger = False
