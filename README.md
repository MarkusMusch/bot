
# Trading Bot

**One-stop toolkit for fully automated algorithmic trading.**

**Includes:**

1. Live Trading

	* A REST client to deal with Binance API that you can easily adapt to work with your favorite exchanges' REST APIs.
	* An abstract Strategy class that serves as a template for implementing your own strategies.
	* An example strategy that serves as a blueprint for your own strategies or as a starting point to build upon.
	* A Portfolio class that makes combining your strategies into full portfolios straight forward.

	<p align="center">
	<img src="https://github.com/MarkusMusch/bot/blob/main/images/pnl.jpeg" />
	</p>

    > In the period from 11th of December 2022, when the bot first went live, until 28th of December 2022 it produced a cummulative PnL of 9.59%
    >
    > Note! This repository does not contain my full set of proprietary trading strategies. It only contains one of the strategies which make up my trading portfolio to serve as an example for users. My full portfolio consists of a diversified collection of strategies to maximize risk adjusted returns.

2. Backtesting

	* A Backtest class serving as a template for backtesting any strategy you will implement.
	* Two backtest modules for an example strategy and an example portfolio that you can copy paste and easily adapt to your use case.
	* Backtest reports for the example strategy including plots of the equity curve and important performance metrics for different parameters.

	<p align="center">
	<img src="https://github.com/MarkusMusch/bot/blob/main/images/equity_curve.png" />
	</p>

    > The backtest in the image above shows the returns that would have been achieved with the full portfolio of proprietary trading strategies starting 21st of February 2021.

3. Data Handling

	* A DataHandler class that serves as a processing interface between a REST client handling communication with different APIs and your csv data with a unified structure.
    * A datapipline module that can easily be adapted to fetch data of your favorite coin and time frame and store it into a csv file.
	* A collection of csv files with the data of your favorite coins to improve backtesting speed and enable coding work offline.

	<p align="center">
	<img src="https://github.com/MarkusMusch/bot/blob/main/images/backtest_flowchart.png" />
	</p>

    > The above flow chart shows the data flow from the exchange API through the datapipline into the database. From there we load the data to run backtests and produce detailed reports on all our teted strategies.

## Installation

First, clone the repository.

 ```bash
 git clone 'https://github.com/MarkusMusch/bot.git' && cd bot/
 ```
 
 Second, install all third party libraries necessary. Those are all listed in the [requirements.txt](requirements.txt).

 ```bash
 pip install -r requirements.txt
 ```

## Usage

### Live Trading

I personally run this code in the cloud and can help you get started.

If you are serious about setting up my framework on a cloud server, reach out to me on [Linkedin](https://www.linkedin.com/in/dr-markus-musch-b504a21b7/).

### Writing a Strategy

Our example is a strategy that bets on the continuation of an ongoing trend. If the market is in an up-trend, and certain criteria are satisfied, the strategy enters a long trade to profit from the continuation of the up-trend. In the same way, we enter a short trade if the market is in an ongoing down-trend and certain criteria are satisfied.

Whilst the abstract strategy class is in the /bot/src/ directory, the actual implementation of a particular strategy is in the /bot/src/strategies directory. 

So, to implement our trend continuation strategy we create a new file in the /bot/src/strategies directory. In our case it is called ContinuationTrade.py. In this file we implement the trade logic in a class that inherits from Strategy.

<p align="center">
  <img src="https://github.com/MarkusMusch/bot/blob/main/images/strategy_inheritance.png">
</p>

### Assembling a Full Portfolio for Live Trading
To assemble your portfolio, define your tradable assets in Assets.py. Import them into the live.py module like this:

```Python
from  src.Assets  import  btc_cont_live, eth_cont_live, sol_cont_live, \
						  doge_cont_live
```

and define the markets you want to trade in the main function

```Python
if  __name__ == '__main__':

	markets = [btc_cont_live, eth_cont_live, sol_cont_live, doge_cont_live]

	portfolio = initialize_portfolio(markets, live=True)

	trade(portfolio)
```

### Writing Backtests: Single Strategies and Full Portfolios

#### Single Strategy Backtest
To set up a new backtest for an individual strategy, you will create a new .py file in the /bot/back_tests/ directory with the name of your backtest.

You can copy paste the code from the exisiting backtest_continuation_trade.py module. In this module, we backtest the continuation trade strategy. For this we import the ContinuationTrade class like this:

```Python
from  src.strategies.ContinuationTrade  import  ContinuationTrade
```

You will replace this import line with the module and class of your own strategy. You can also change the preset list of markets and adjust the set of risk levels, leverage sizes, and reward/risk ratios if the predefined ones do not fit your particular use case.

```Python  
markets = [btc_cont, eth_cont, sol_cont, doge_cont]

risk_samples = [0.001, 0.005 , 0.01, 0.05, 0.1, 0.2]
leverage_samples = [1 , 3, 5, 10]
risk_reward = [2.0, 3.0]
```
If you want to trade markets that are not included in the current code, make sure to define them in the Assets.py module and import them.

The last step is to loop through all markets and run the backtests. Here you have to change the second argument "ContinuationTrade" to be your strategy.

```Python
for  market  in  markets:
	bt.run(ec, ContinuationTrade, market, risk_samples, leverage_samples,
		   risk_reward, Timeframes)
```
The Backtest object will also save a report of you backtest in the /bot/back_tests/backtest_reports/ directory including equity curves and the most important performance metrics such as Sharpe ratio, Sortino ratio, and maximum draw down of your test run.

<p align="center">
  <img src="https://github.com/MarkusMusch/bot/blob/main/images/single_strat_backtest.png">
</p>

#### Full Portfolio Backtest

Setting up a full portfolio backtest works almost the same way as setting up a portfolio for live trading which has been explained above.

To assemble your portfolio, define your tradable assets in Assets.py. Import them into the backtest_portfolio.py module like this:

```Python
from  src.Assets  import  btc_cont, eth_cont, sol_cont, doge_cont
```

and define the markets you want to trade in the main function

```Python
if  __name__ == '__main__':

markets = [btc_cont, eth_cont, sol_cont, doge_cont]

portfolio = initialize_portfolio(markets, live=False)
```
The only difference to setting up a live trading portfolio is that we set the live parameter to ```False``` when initializing the portfolio and not calling the trade function that initiate the scheduler for live trading.

<p align="center">
  <img src="https://github.com/MarkusMusch/bot/blob/main/images/portfolio_backtest.png">
</p>

### Getting Data

In Assets.py instantiate an object representing your asset. For a continuation trade on Bitcoin we do it like this:

```Python
btc_cont = Asset(ContinuationTrade, 'Continuation_Trade', 'BTCBUSD',
				 (58434.0, '2021-02-21 19:00:00+00:00'),
				 (57465.0, '2021-02-21 18:00:00+00:00'),
				 datetime(2021, 2, 21, 20, 0, 0, 0), 100,
				 Timeframes.ONE_HOUR.value, 0.1, 1.0, 2.0, 3)
```

In the datapipline.py module we define the tickers we are interested in.


```Python
busd_markets = ['BTCBUSD', 'ETHBUSD', 'SOLBUSD', 'DOGEBUSD']
```

In our case we are interested in the BUSD futures for $BTC, $ETH, $SOL, and $DOGE. If you are interested in other coins you can find out their ticker on your exchanges' website and replace them in the list above. Make sure to also adapt the classes in the RESTClient.py module if you are using another exchange.

Now we only need to run
```bash
Python3 datapipeline.py
```

from the /bot directory and it will load the requested data from the Binance futures API into csv files located in the /bot/database/datasets directory.

By default, the time frames 1d, 1h, and 4h are implemented but if you are interested in other time frames you can easily extend the Enum

```Python
class  Timeframes(Enum):
	ONE_HOUR = '1h'
	FOUR_HOURS = '4h'
	ONE_DAY = '1d'
```

in Assets.py.

If, for example, you wanted to add the 5m time frame, you would simply add the line

```Python
FIVE_MINUTES = '5m'
```
in the Enum in Assets.py and the lines

```Python
download(market, Timeframes.FIVE_MINUTES.value, timedelta(minutes=4999))
print(Timeframes.FIVE_MINUTES.value + ' done! \n')
```
The ```timedelta``` this way since we can at most request 1000 data entries at a time from the Binance API. By default it is 500 data entries, but by explicitly requesting 1000 we can reduce the number of requests and therefore the time it takes to download our data.

## Contributing

1. Fork it (https://github.com/MarkusMusch/bot/fork)
2. Create your feature branch (git checkout -b feature/fooBar)
3. Commit your changes (git commit -am 'Add some fooBar')
4. Push to the branch (git push origin feature/fooBar')
5. Create a new Pull Request

If you are serious about  contributing to the project or you have a similar project and are keen to discuss coding or trading, reach out to me on [Linkedin](https://www.linkedin.com/in/dr-markus-musch-b504a21b7/).

## License and author info

### Author

Markus Musch: [Linkedin](https://www.linkedin.com/in/dr-markus-musch-b504a21b7/)

### License

See the [LICENSE](LICENSE.md) file for license rights and limitations (GNU GPLv3).
