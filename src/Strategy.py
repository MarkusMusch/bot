"""Implement an abstract class as a template for particular strategies.

Classes
----------
    Strategy:
        Implements generic properties of strategies that are
        common amongst all particular trading strategies
        such as buying and selling.
"""

import os
import logging
import configparser
from typing import Any
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests

from src.MarketStructure import MarketStructure
from src.RESTClient import RESTClient


class Strategy(ABC):
    """Implements generic functions of trades that are common amongst all
    particular trading strategies such as buying and selling.

    ...

    Attributes
    ----------
    ms : MarketStructure
        MarketStructure object representing the market structure.
    ec : RESTClient
        RESTClient object to fetch data.
    equity_curve : np.array
        The equity curve of the strategy.
    position_size : list
        The size of the position at each time step.
    num_trades : int
        The number of trades executed.
    wins : int
        The number of winning trades.
    win_rate : float
        The win rate of the strategy.

    Methods
    -------
    equity -> float:
        Returns the current equity of the strategy.
    plot_equity() -> None:
        Plots the equity curve of the strategy.
    plot_position_size() -> None:
        Plots the position size of the strategy.
    """

    def __init__(self, ec: RESTClient, ms: MarketStructure, strat_name: str,
                 asset: dict, market_name: str, equity: float,
                 max_risk: float, max_leverage: float = 1.0,
                 timeframe: str = '1h', live: bool = False):
        """
        Parameters
        ----------
        ec : RESTClient
            RESTClient object to fetch data.
        ms : MarketStructure
            MarketStructure object representing the market structure.
        strat_name : str
            Name of the strategy.
        asset : dict
            Dictionary of asset information.
        market_name : str
            Name of the market.
        equity : float
            Initial equity of the strategy.
        max_risk : float
            Maximum risk per trade.
        max_leverage : float
            Maximum leverage of the strategy.
        timeframe : str
            Timeframe of the strategy.
        live : bool
            Whether the strategy is live or not.
        """

        self.ms = ms
        self.ec = ec
        self.timeframe = timeframe
        self.equity_curve = np.array([equity])
        self.position_size = [0]
        self.num_trades = 0
        self.wins = 0
        self.win_rate = 0
        self._strat_name = strat_name
        self._position = 0
        self._long_trigger = False
        self._long_position = False
        self._short_trigger = False
        self._short_position = False
        self._entry = None
        self._stop_loss = None
        self._target = None
        self._live = live
        self._asset = asset
        self._equity = asset.initial_equity

    @abstractmethod
    def next_candle_init(self, row: pd.Series) -> None:
        """Initializes the strategy by iterating through historical data
        without executing trades."""

        pass

    @abstractmethod
    def next_candle_live(self, row: pd.Series) -> None:
        """Checks for valid trade set ups with new live data and execute
        live trades."""

        pass

    @property
    def equity(self) -> float:
        """Returns the current equity value of the strategy.

        Returns
        -------
        float
            The current equity value of the strategy.
        """

        if self._long_position or self._short_position:
            return (self._position*self.close) + self._equity
        else:
            return self._equity

    def plot_equity_curve(self) -> None:
        """Plots the equity curve of the strategy."""

        plt.plot(self.equity_curve)
        plt.show()

    def plot_position_size(self) -> None:
        """Plots the position size of the strategy over time."""

        plt.plot(self._position_size)
        plt.show()

    def _send_message(self, message: str) -> Any:
        """Send a message to telegram.

        Parameters
        ----------
        message : str
            The message to send.

        Returns
        -------
        Any
            The response from the telegram API.
        """

        config = configparser.ConfigParser()
        config.read(os.path.expanduser('~') + '/config.ini')

        bot_token = config['Telegram']['bot_token']
        group_id = config['Telegram']['group_id']

        params = {'chat_id': group_id, 'text': message, 'parse_mode': 'HTML'}
        response = requests.post('https://api.telegram.org/bot{}/sendMessage'
                                 .format(bot_token), params)

        return response

    def _long(self, price: float, risk: float) -> None:
        """Enters a long trade.

        Parameters
        ----------
        price : float
            The price at which to buy the asset.
        risk : float
            The risk per trade.
        """

        trade_size = min(self._asset.max_leverage*self._equity,
                         (self._asset.max_risk/risk) * self._equity)
        coins = round(trade_size/price, self._asset.decimals)
        self._position += coins
        self._equity -= (1.+self.ec.taker_fees_USD_futures) \
            * coins*price
        if self._live:
            self._send_message("Initiate New Long Position For "
                               + self._strat_name +
                               ", " + self._asset.market_name)
            response = self.ec.place_order(self._asset.market_name,
                                           'BUY', coins,
                                           reduce_only=False,
                                           order_type='MARKET')
            if 'code' in response:
                self._send_message('Trade Execution Failed: '
                                   + response['msg'])
                self._equity += (1.+self.ec.taker_fees_USD_futures) \
                    * coins*price
                self._position -= coins
            else:
                self._send_message("New Long Position Opened: \n"
                                   + "entry: " + str(price) + "\n"
                                   + "stop loss: " + str(self._stop_loss)
                                   + "\n"
                                   + "target: " + str(self._target) + "\n"
                                   + "coins: " + str(coins) + "\n"
                                   + "trade_size: " + str(trade_size) + "\n"
                                   + "position: " + str(self._position) + "\n"
                                   + "equity: " + str(self._equity) + "\n")
                logging.info('New Long Position Opened on Exchange')
        logging.info('Entered New Long Position')

    def _short(self, price: float, risk: float) -> None:
        """Enters a short trade.

        Parameters
        ----------
        price : float
            The price at which to sell the asset.
        risk : float
            The risk per trade.
        """

        trade_size = min(self._asset.max_leverage*self._equity,
                         (self._asset.max_risk/risk) * self._equity)
        coins = round(trade_size/price, self._asset.decimals)
        self._position -= coins
        self._equity += (1.-self.ec.taker_fees_USD_futures) * coins*price
        if self._live:
            self._send_message("Initiate New Short Position For "
                               + self._strat_name +
                               ", " + self._asset.market_name)
            response = self.ec.place_order(self._asset.market_name,
                                           'SELL', coins,
                                           reduce_only=False,
                                           order_type='MARKET')
            if 'code' in response:
                self._send_message('Trade Execution Failed: '
                                   + response['msg'])
                self._equity -= (1.-self.ec.taker_fees_USD_futures) \
                    * coins*price
                self._position += coins
            else:
                self._send_message("New Short Position Opened: \n"
                                   + "entry: " + str(price) + "\n"
                                   + "stop loss: " + str(self._stop_loss)
                                   + "\n"
                                   + "target: " + str(self._target) + "\n"
                                   + "coins: " + str(coins) + "\n"
                                   + "trade_size: " + str(trade_size) + "\n"
                                   + "position: " + str(self._position) + "\n"
                                   + "equity: " + str(self._equity) + "\n")
                logging.info('New Short Position Opened on Exchange')
        logging.info('Entered New Short Position')

    def _close_long_trade(self, price: float) -> None:
        """Closes an open long or short positoin.

        Parameters
        ----------
        price : float
            The price at which to close the position.
        """

        coins = self._position
        cash = self._position*price
        self._equity += (1.-self.ec.taker_fees_USD_futures) * cash
        if self._live:
            self._send_message("Closing Long Position For "
                               + self._strat_name + ", " +
                               self._asset.market_name)
            response = self.ec.place_order(self._asset.market_name, 'SELL',
                                           self._position, reduce_only=True,
                                           order_type='MARKET')
            if 'code' in response:
                self._send_message('Trade Execution Failed: '
                                   + response['msg'])
                self._equity -= (1.-self.ec.taker_fees_USD_futures) * cash
                self._position = coins
            else:
                self._send_message("Long Position Closed Sucessfully: "
                                   + self._strat_name + ", "
                                   + self._asset.market_name + "\n"
                                   + "position: " + str(self._position) + "\n"
                                   + "equity: " + str(self._equity) + "\n")
                logging.info('Long Position Closed on Exchange')
        self._position = 0

    def _close_short_trade(self, price: float) -> None:
        """Closes an open long or short positoin.

        Parameters
        ----------
        price : float
            The price at which to close the position.
        """

        coins = self._position
        cash = self._position*price
        self._equity += (1.-self.ec.taker_fees_USD_futures) * cash
        if self._live:
            self._send_message("Closing Short Position For "
                               + self._strat_name + ", " +
                               self._asset.market_name)
            response = self.ec.place_order(self._asset.market_name, 'BUY',
                                           -self._position,
                                           reduce_only=True,
                                           order_type='MARKET')
            if 'code' in response:
                self._send_message('Trade Execution Failed: '
                                   + response['msg'])
                self._equity -= (1.-self.ec.taker_fees_USD_futures) * cash
                self._position = coins
            else:
                self._send_message("Short Position Closed Sucessfully: "
                                   + self._strat_name + ", "
                                   + self._asset.market_name + "\n"
                                   + "position: " + str(self._position)
                                   + "\n"
                                   + "equity: " + str(self._equity) + "\n")
                logging.info('Short Position Closed on Exchange')
        self._position = 0

    @abstractmethod
    def _entry_long(self, row: pd.Series) -> None:
        """Looking for an entry to a long trade after a signal has been
        triggered."""

        pass

    @abstractmethod
    def _exit_long(self, row: pd.Series) -> None:
        """Checks if an open long trade has to be closed."""

        pass

    @abstractmethod
    def _entry_short(self, row: pd.Series) -> None:
        """Looking for an entry to a short trade after a signal has been
        triggered."""

        pass

    @abstractmethod
    def _exit_short(self, row: pd.Series) -> None:
        """Checks if an open short trade has to be closed."""

        pass

    @abstractmethod
    def _setup_trade(self, row: pd.Series) -> None:
        """Activates trade triggers and sets stop losses."""

        pass

    @abstractmethod
    def _execute_trade(self, row: pd.Series) -> None:
        """Enters trade after triggered and follows through until trade
        exit."""

        pass
