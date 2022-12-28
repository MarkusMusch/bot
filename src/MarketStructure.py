"""Implement classes to represent market structure.

Classes
----------
MarketStructure:
    Represents the market structure of a crypto coin
    at one point in time.
"""

import logging
from typing import Any

import pandas as pd


class MarketStructure:
    """Represent the market structure of an asset at one point in time.

    ...

    Attributes
    ----------
    msb : bool
        True if the market structure broke recently.
    stay_in_range : bool
        True if the market structure stayed in range recently.
    continuation : bool
        True if the market structure continued recently.
    trend : bool
        True if the market structure is in an up trend.
    prev_high : tuple
        The previous high of the market structure.
    prev_low : tuple
        The previous low of the market structure.
    provisional_high : tuple
        The provisional high of the market structure.
    provisional_low : tuple
        The provisional low of the market structure.

    Methods
    -------
    next_candle(row: pd.Series) -> Any:
        Investigates how the market structure changes with the next
        incoming price data candle.
    """

    def __init__(self, prev_high: tuple, prev_low: tuple,
                 provisional_high: tuple, provisional_low: tuple):
        """
        Parameters
        ----------
        prev_high : tuple
            The previous high of the market structure.
        prev_low : tuple
            The previous low of the market structure.
        provisional_high : tuple
            The provisional high of the market structure.
        provisional_low : tuple
            The provisional low of the market structure.
        """

        self.msb = False
        self.stay_in_range = False
        self.continuation = False
        self.trend = False
        self.prev_high = prev_high
        self.prev_low = prev_low
        self.provisional_high = provisional_high
        self.provisional_low = provisional_low

    def next_candle(self, row: pd.Series) -> Any:
        """Investigates how the market structure changes

        Investigates how the market structure changes with the next
        incoming price data candle.

        Parameters
        ----------
        row : pd.Series
            The next incoming price data candle.

        Returns
        -------
        bool
            True if the market structure is in an up trend.
        bool
            True if the market structure broke recently.
        bool
            True if the market structure continued recently.
        """

        close = row['close']
        self.msb = False
        self.continuation = False
        self.stay_in_range = False
        trend = self.trend

        if close > self.prev_high[0]:
            if self.trend is False:
                self._break_down_trend(row)
                self.msb = True
            else:
                self._continue_up_trend(row)
                self.continuation = True
        elif close < self.prev_low[0]:
            if self.trend is False:
                self._continue_down_trend(row)
                self.continuation = True
            else:
                self._break_up_trend(row)
                self.msb = True
        else:
            self._stay_in_range(row)
            self.stay_in_range = True

        logging.info(f'prev_high: {self.prev_high} \n prev_low: '
                     + f'{self.prev_low} \n provisional_high: '
                     + f'{self.provisional_high} \n provisional_low: '
                     + f'{self.provisional_low}')

        return trend, self.msb, self.continuation, self.stay_in_range

    @property
    def structure(self):
        """Prints the market structure."""

        prev_high_ts = str(pd.to_datetime(self.prev_high[1]*1000000))
        prev_low_ts = str(pd.to_datetime(self.prev_low[1]*1000000))
        prv_h_ts = str(pd.to_datetime(self.provisional_high[1]*1000000))
        prv_l_ts = str(pd.to_datetime(self.provisional_low[1]*1000000))

        print('Market Structure: \n'
              + f'high: {(self.prev_high[0], prev_high_ts)} \n'
              + f'low: {(self.prev_low[0], prev_low_ts)} \n'
              + f'provisional_high: {(self.provisional_high[0], prv_h_ts)} \n'
              + f'provisional_low: {(self.provisional_low[0], prv_l_ts)} \n')

    def _break_up_trend(self, row: pd.Series) -> None:
        """Sets the new market structure after break of an up trend.

        Parameters
        ----------
        row : pd.Series
            The next incoming price data candle.
        """

        self.trend = False
        self.prev_high = self.provisional_high
        self.prev_low = tuple(row[['low', 'open time']])
        self.provisional_low = tuple(row[['low', 'open time']])
        logging.info('Up Trend Broken')

    def _break_down_trend(self, row: pd.Series) -> None:
        """Sets the new market structure after break of a down trend.

        Parameters
        ----------
        row : pd.Series
            The next incoming price data candle.
        """

        self.trend = True
        self.prev_high = tuple(row[['high', 'open time']])
        self.prev_low = self.provisional_low
        self.provisional_high = tuple(row[['high', 'open time']])
        logging.info('Down Trend Broken')

    def _continue_up_trend(self, row: pd.Series) -> None:
        """Sets the new market structure after an up trend continues.

        Parameters
        ----------
        row : pd.Series
            The next incoming price data candle.
        """

        self.prev_low = self.provisional_low
        self.prev_high = tuple(row[['high', 'open time']])
        self.provisional_high = tuple(row[['high', 'open time']])
        logging.info('Continuing Up Trend')

    def _continue_down_trend(self, row: pd.Series) -> None:
        """Sets the new market structure after a down trend continues.

        Parameters
        ----------
        row : pd.Series
            The next incoming price data candle.
        """

        self.prev_high = self.provisional_high
        self.prev_low = tuple(row[['low', 'open time']])
        self.provisional_low = tuple(row[['low', 'open time']])
        logging.info('Continuing Down Trend')

    def _stay_in_range(self, row: pd.Series) -> None:
        """Keeps track of provisional information while range bound.

        Parameters
        ----------
        row : pd.Series
            The next incoming price data candle.
        """

        if row['close'] - row['open'] >= 0:
            self.provisional_high = tuple(row[['high', 'open time']])
        if row['close'] - row['open'] < 0:
            self.provisional_low = tuple(row[['low', 'open time']])
        logging.info('Staying in Range')
