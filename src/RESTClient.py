"""Implement classes for communication with APIs.

Implement classes to gather data and execute trades on exchanges by
communicating via API.

Classes
----------
    RESTClient:
        Provide a Client for REST APIs.
    ExchangeClient:
        Provides an interface for the trading bot to communicate
        with an exchange via its' API.
"""

import configparser
import logging
import os
import time

from typing import Any
import hashlib
import hmac
import requests
from requests import Response
from urllib.parse import urlencode


class RESTClient:
    """Provide a Client for REST APIs.

    Provide an interface to communicate with REST APIs for data collection
    and trading.

    ...

    Methods
    -------
    get_data(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        Executes an HTTPS GET request to get data from the exchange.
    """

    def __init__(self, endpoint: str):
        """
        Parameters
        ----------
        endpoint : str
            The endpoint of the API.
        path : str
            The path to the data API.
        """

        self._endpoint = endpoint


class DataClient(RESTClient):
    """Provide a Client for REST APIs to collect data.

    ...

    Methods
    -------
    get_data(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        Executes an HTTPS GET request to get data from the exchange.
    """

    def __init__(self, endpoint: str, path: str):
        """
        Parameters
        ----------
        endpoint : str
            The endpoint of the API.
        path : str
            The path to the data API.
        """

        super().__init__(endpoint)
        self._data_path = path

    def get_data(self, params: dict) -> Any:
        """Executes an HTTPS GET request.

        Parameters
        ----------
        path : str
            The path of the request.
        params : Optional[Dict[str, Any]]
            The parameters of the request.

        Returns
        -------
        Any
            The response of the request.
        """

        try:
            response = requests.get(self._endpoint + self._data_path, params)
        except requests.exceptions.Timeout:
            logging.warning("Request has timed out")
        except requests.exceptions.ConnectionError:
            logging.warning("Request has faced a connection error")

        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            return data


class TradeClient(DataClient):
    """Provide an interface for the trading bot to communicate with an
    exchange.

    ...

    Methods
    -------
    read_config() -> None:
        Initializes the Exchange client.
    place_order(market: str, side: str, size: float, reduce_only: bool = False,
                order_type: str = 'MARKET') -> dict:
        Places a buy or sell order with the exchange.
    """

    def __init__(self, endpoint: str, data_path: str, trade_path: str,
                 api: str, maker_fees: float, taker_fees: float):

        """
        Parameters
        ----------
        endpoint : str
            The endpoint of the exchange.
        data_path : str
            The path to the data API.
        trade_path : str
            The path to the trade API.
        api : str
            The name of the exchange.
        maker_fees : float
            The maker fees of the exchange for futures.
        taker_fees : float
            The taker fees of the exchange for futures.
        """

        super().__init__(endpoint, data_path)
        self.maker_fees_USD_futures = maker_fees
        self.taker_fees_USD_futures = taker_fees
        self._trade_path = trade_path
        self._api = api
        self._config = None
        self._api_key = None
        self._api_secret = None

    def read_config(self) -> None:
        """Initializes the Exchange client."""

        self._config = configparser.ConfigParser()
        self._config.read(os.path.expanduser('~') + '/config.ini')

        self._api_key = self._config[self._api]['api_key']
        self._api_secret = self._config[self._api]['api_secret']

    def _place_order(self, params: dict) -> Response:
        """
        Send HTTPS post to exchange for order placement.

        Parameters
        -------
        params: dict
            Dictionary of order parameters.

        Returns
        -------
        Response
            The response of the request.
        """

        headers = {'X-MBX-APIKEY': self._api_key}

        ts = int(time.time() * 1000)
        params['timestamp'] = ts

        signature = hmac.new(self._api_secret.encode('utf-8'),
                             urlencode(params).encode('utf-8'),
                             hashlib.sha256).hexdigest()
        params['signature'] = signature

        try:
            response = requests.post(self._endpoint + self._trade_path,
                                     params=params, headers=headers)
        except requests.exceptions.Timeout:
            logging.warning("Attempt at placing an order has timed out")
        except requests.exceptions.ConnectionError:
            logging.warning("Attempt at placing and order has faced a "
                            + "connection error")

        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            return data


class BinanceFuturesClient(TradeClient):
    """
    Hold key information for Binance Futures Exchange.

    Attributes
    ----------
    maker_fees_USD_futures : float
        The maker fees for the exchange in USD.
    taker_fees_USD_futures : float
        The taker fees for the exchange in USD.
    """

    def __init__(self):

        super().__init__('https://fapi.binance.com/', 'fapi/v1/klines',
                         'fapi/v1/order', 'BINANCE_FUTURES', maker_fees=0.0002,
                         taker_fees=0.0004)

    def place_order(self, market: str, side: str, size: float,
                    reduce_only: bool = False,
                    order_type: str = 'MARKET') -> dict:
        """
        Pair order parameters with parameter names of this exchange.

        Parameters
        ----------
        market : str
            The ticker or the market to trade on.
        side : str
            The side of the order, either 'BUY' or 'SELL'.
        size : float
            The size of the order.
        reduce_only : bool
            Whether the order should be a reduce only order.
        order_type : str
            The type of the order, either 'MARKET' or 'LIMIT'.
        """

        params = {
            'symbol': market,
            'side': side,
            'type': order_type,
            'quantity': size,
            'reduceOnly': reduce_only,
        }

        return self._place_order(params)


class BinanceSpotClient(DataClient):
    """
    Hold key information for Binance Spot Exchange.
    """

    def __init__(self):
        super().__init__('https://api.binance.com/', 'api/v3/klines')


class CoinglassOIClient(DataClient):
    """
    Hold key information for Coinglass API.
    """

    def __init__(self):
        super().__init__('https://open-api.coinglass.com',
                         'api/pro/v1/futures/openInterest/chart')


class ByBitSpotClient(DataClient):
    """
    Hold key information for ByBit Spot Exchange.
    """

    def __init__(self):
        super().__init__('https://api.bybit.com',
                         'spot/v3/public/quote/kline')


class ByBitFuturesClient(DataClient):
    """
    Hold key information for ByBit Futures Exchange.
    """

    def __init__(self):
        super().__init__('https://api.bybit.com', 'public/linear/kline')
