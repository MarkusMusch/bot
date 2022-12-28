"""Implement classes for data handling.

Implements a class to manage price data and calculate and add other
data such as OI, funding, and CVD.

Classes
----------
    DataHandler:
        Request data from different APIs and stores it in a dataframe.
"""

from datetime import datetime, timedelta

import pandas as pd

from src.RESTClient import RESTClient


class DataHandler:
    """Store price data and calculate and add other data such as OI,
    funding, and CVD.

    ...

    Methods
    -------
    fetch_historical_data(ec: RESTClient, market_name: str,
                        timeframe: str, start_time: datetime,
                        end_time: datetime) -> pd.DataFrame:
        Fetches historical data from the exchange via RESTClient.
    fetch_current_data(ec: RESTClient, market_name: str,
                        timeframe: str) -> pd.DataFrame:
        Fetches current data from the exchange via RESTClient.
    aggregate_data(quotes: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        Aggregates the data to the specified timeframe.
    """

    def __init__(self, vd: bool = False) -> None:
        """
        Parameters
        ----------
        vd : bool
            Whether to calculate volume delta.
        funding : bool
            Whether to calculate funding.
        """

        self._vd = vd

    def _compute_vd_helper(self, volume: float,
                           taker_buy_volume: float) -> float:
        """Computes the volume delta for a given candle.

        Parameters
        ----------
        volume : float
            The volume of the candle.
        taker_buy_volume : float
            The taker buy volume of the candle.

        Returns
        -------
        float
            The volume delta of the candle.
        """

        vd = 2*taker_buy_volume - volume
        return vd

    def _compute_vd(self, quotes: pd.DataFrame) -> pd.DataFrame:
        """Computes the volume delta for a given dataframe.

        Parameters
        ----------
        quotes : pd.DataFrame
            The dataframe containing the price data.

        Returns
        -------
        pd.DataFrame
            The dataframe containing the price data with volume delta.
        """

        quotes['volume_delta_base_asset'] = \
            quotes.apply(lambda x:
                         self._compute_vd_helper(x.volume,
                                                 x.taker_buy_base_asset_volume),
                         axis=1)
        quotes['volume_delta_quote_asset'] = \
            quotes.apply(lambda x:
                         self._compute_vd_helper(x.quote_asset_volume,
                                                 x.taker_buy_quote_asset_volume),
                         axis=1)

        return quotes

    def _compute_vd_ma(self, quotes: pd.DataFrame,
                       window: int) -> pd.DataFrame:
        """Computes the volume delta moving average for a given dataframe.

        Parameters
        ----------
        quotes : pd.DataFrame
            The dataframe containing the price data.

        Returns
        -------
        pd.DataFrame
            The dataframe containing the price data with volume delta moving
            average.
        """

        quotes['volume_delta_moving_average_base_asset'] = \
            quotes['volume_delta_base_asset'].rolling(window=window).sum()
        quotes['volume_delta_moving_average_quote_asset'] = \
            quotes['volume_delta_quote_asset'].rolling(window=window).sum()

        return quotes

    def _compute_cvd(self, quotes: pd.DataFrame) -> pd.DataFrame:
        """Computes the cumulative volume delta for a given dataframe.

        Parameters
        ----------
        quotes : pd.DataFrame
            The dataframe containing the price data.

        Returns
        -------
        pd.DataFrame
            The dataframe containing the price data with cumulative volume
            delta.
        """

        quotes['cvd_base_asset'] = quotes['volume_delta_base_asset'].cumsum()
        quotes['cvd_quote_asset'] = quotes['volume_delta_quote_asset'].cumsum()

        return quotes

    def fetch_historical_data(self, ec: RESTClient, market_name: str,
                              timeframe: str, start_time: datetime,
                              end_time: datetime) -> pd.DataFrame:
        """Fetches historical data from the exchange via RESTClient.

        Parameters
        ----------
        ec : RESTClient
            The exchange client to use.
        market_name : str
            The ticker of the market to fetch data for.
        timeframe : str
            The timeframe to fetch data for.
        start_time : datetime
            The start time of the data to fetch.
        end_time : datetime
            The end time of the data to fetch.

        Returns
        -------
        pd.DataFrame
            The dataframe containing the price data.
        """

        response = ec.get_data({'symbol': market_name, 'interval': timeframe,
                                'startTime':
                                str(int(start_time.timestamp()*1000)),
                                'endTime':
                                str(int(end_time.timestamp()*1000)),
                                'limit': '1000'})

        quotes = pd.DataFrame(response,
                              columns=['open time', 'open', 'high', 'low',
                                       'close', 'volume', 'close time',
                                       'quote_asset_volume',
                                       'number of trades',
                                       'taker_buy_base_asset_volume',
                                       'taker_buy_quote_asset_volume',
                                       'unused field'])

        quotes[['open', 'high', 'low', 'close', 'volume',
                'quote_asset_volume', 'taker_buy_base_asset_volume',
                'taker_buy_quote_asset_volume']] \
            = quotes[['open', 'high', 'low', 'close', 'volume',
                      'quote_asset_volume', 'taker_buy_base_asset_volume',
                      'taker_buy_quote_asset_volume']].astype(float)

        if self._vd:
            quotes = self._compute_vd(quotes)

        return quotes

    def fetch_current_data(self, ec: RESTClient, market_name: str,
                           timeframe: str) -> pd.DataFrame:
        """Fetches current data from the exchange via RESTClient.

        Parameters
        ----------
        ec : RESTClient
            The exchange client to use.
        market_name : str
            The ticker of the market to fetch data for.
        timeframe : str
            The timeframe to fetch data for.

        Returns
        -------
        pd.DataFrame
            The dataframe containing the price data.
        """

        response = ec.get_data({'symbol': market_name, 'interval': timeframe})

        quotes = pd.DataFrame(response,
                              columns=['open time', 'open', 'high', 'low',
                                       'close', 'volume', 'close time',
                                       'quote_asset_volume',
                                       'number of trades',
                                       'taker_buy_base_asset_volume',
                                       'taker_buy_quote_asset_volume',
                                       'unused field'])

        quotes[['open', 'high', 'low', 'close', 'volume',
                'quote_asset_volume', 'taker_buy_base_asset_volume',
                'taker_buy_quote_asset_volume']] \
            = quotes[['open', 'high', 'low', 'close', 'volume',
                      'quote_asset_volume', 'taker_buy_base_asset_volume',
                      'taker_buy_quote_asset_volume']].astype(float)

        quotes['datetime'] = pd.to_datetime(quotes['open time'], unit='ms')

        if self._vd:
            quotes = self._compute_vd(quotes)

        return quotes

    def aggregate_data(self, ec: RESTClient, market_name: str,
                       timeframe: str, start_time: datetime,
                       delta: timedelta) -> pd.DataFrame:
        """Aggregates the data from several requests.

        Parameters
        ----------
        ec : RESTClient
            The exchange client to use.
        market_name : str
            The ticker of the market to fetch data for.
        timeframe : str
            The timeframe to fetch data for.
        start_time : datetime
            The start time of the data to fetch.

        Returns
        -------
        pd.DataFrame
            The dataframe containing the price data.
        """

        start_time = start_time
        end_time = start_time + delta

        df = pd.DataFrame()

        while start_time < datetime.now():

            tmp_df = self.fetch_historical_data(ec, market_name, timeframe,
                                                start_time, end_time)

            df = pd.concat([df, tmp_df], ignore_index=True)

            start_time = end_time
            end_time = end_time + delta

        return df
