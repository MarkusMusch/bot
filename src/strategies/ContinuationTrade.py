"""Implement an implementation of Strategy for a continuation trade.

Classes
----------
    ContinuationTrade:
        Implement the buy and sell logic of a continuation trade.
"""

import logging

import numpy as np
import pandas as pd

from dataclasses import dataclass
from src.MarketStructure import MarketStructure
from src.RESTClient import RESTClient
from src.Strategy import Strategy


class ContinuationTrade(Strategy):
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

    def __init__(self, ec: RESTClient, ms: MarketStructure, asset: dataclass,
                 live: bool = False, message: bool = True):
        """
        Parameters
        ----------
        ec : RESTClient
            Exchange client to interact with the exchange.
        ms : MarketStructure
            Represent the market structure of the asset.
        asset : dict
            Asset to trade.
        live : bool, optional
            Whether the strategy is live or not, by default False
        message : bool, optional
            Whether to send messages to Telegram, by default True
        """

        super().__init__(ec, ms, asset, live, message)
        self._risk_reward = asset.risk_reward

    def next_candle_init(self, row: pd.Series) -> None:
        """Initializes the strategy by iterating through historical data
        without executing trades.

        Parameters
        ----------
        row : pd.Series
            Row of historical data.
        """

        self._setup_trade(row)

    def next_candle_live(self, row: pd.Series) -> None:
        """Checks for valid trade set ups with new live data and execute live
        trades.

        Parameters
        ----------
        row : pd.Series
            Row of live data.
        """

        self._execute_trade(row)
        self._setup_trade(row)

    def _entry_long(self, row: pd.Series) -> None:
        """Looking for an entry to a long trade after a signal has been
        triggered.

        Parameters
        ----------
        row : pd.Series
            Row of live data.
        """

        price = row['close']
        if price <= self.ms.prev_low[0]:
            self._long_trigger = False
        elif price >= self.ms.prev_high[0] and not self.ms.continuation:
            self._long_trigger = False
        else:
            if price <= self._entry:
                target = self.ms.prev_high[0]
                risk = price - self._stop_loss
                reward_risk = (target - price)/risk
                if reward_risk >= self._risk_reward:
                    self._target = target
                    self._long(price, risk/price)
                    self.num_trades += 1
                    self._long_position = True
                    self._long_trigger = False

    def _exit_long(self, row: pd.Series) -> None:
        """Checks if an open long trade has to be closed.

        Parameters
        ----------
        row : pd.Series
            Row of live data.
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
            Row of live data.
        """

        price = row['close']
        if price >= self.ms.prev_high[0]:
            self._short_trigger = False
        elif price <= self.ms.prev_low[0] and not self.ms.continuation:
            self._short_trigger = False
        else:
            if price >= self._entry:
                risk = self._stop_loss - price
                reward_risk = (price - self.ms.prev_low[0])/risk
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
            Row of live data.
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
            Row of live data.
        """

        trend, msb, continuation, stay_in_range = self.ms.next_candle(row)
        self.close = row['close']

        if continuation and trend:
            self._entry = 0.66*self.ms.prev_low[0] + 0.33*self.ms.prev_high[0]
            self._stop_loss = self.ms.prev_low[0]
            self._long_trigger = True
        elif continuation and (not trend):
            self._entry = 0.66*self.ms.prev_high[0] + 0.33*self.ms.prev_low[0]
            self._stop_loss = self.ms.prev_high[0]
            self._short_trigger = True

        if not self._live:
            self.position_size.append(self._position)
            self.equity_curve = np.append(self.equity_curve, self.equity)

    def _execute_trade(self, row: pd.Series) -> None:
        """Enters trade after triggered and follows through until trade exit.

        Parameters
        ----------
        row : pd.Series
            Row of live data.
        """

        if self._long_trigger:
            self._entry_long(row)
        if self._long_position:
            self._exit_long(row)
        if self._short_trigger:
            self._entry_short(row)
        if self._short_position:
            self._exit_short(row)
