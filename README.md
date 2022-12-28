
# Trading Bot

**One-stop toolkit for fully automated algorithmic trading.**

**Includes:**

1. Live Trading

	* A REST client to deal with Binance API that you can easily adapt to work with your favorite exchanges' REST APIs.
	* An abstract Strategy class that serves as a template for implementing your own strategies.
	* An example strategy that serves as a blueprint for your own strategies or as a starting point to build upon.
	* A Portfolio class that makes combining your strategies into full portfolios straight forward.

    ![Image](./images/pnl.jpeg)

    > In the period from 11th of December 2022, when the bot first went live, until 28th of December 2022 it produced a cummulative PnL of 9.59%
    >
    > Note! This repository does not contain my full set of proprietary trading strategies. It only contains one of the strategies which make up my trading portfolio to serve as an example for users. My full portfolio consists of a diversified collection of strategies to maximize risk adjusted returns.

2. Backtesting

	* A Backtest class serving as a template for backtesting any strategy you will implement.
	* Two backtest modules for an example strategy and an example portfolio that you can copy paste and easily adapt to your use case.
	* Backtest reports for the example strategy including plots of the equity curve and important performance metrics for different parameters.

    ![Image](./images/portfolio_equity_curve.png)
    ![Image](./images/equity_curve.png)

    > The backtest in the image above shows the returns that would have been achieved with the full portfolio of proprietary strategies starting January 2021.

3. Data Handling

	* A DataHandler class that serves as a processing interface between a REST client handling communication with different APIs and your csv data with a unified structure.
    * A datapipline module that can easily be adapted to fetch data of your favorite coin and time frame and store it into a csv file.
	* A collection of csv files with the data of your favorite coins to improve backtesting speed and enable coding work offline.

    ![Image](./images/Backtest.png)

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

## Getting Data

*Work in progress*

### Writing a Backtest

*Work in progress*

### Writing a Strategy

*Work in progress*

### Assembling a Portfolio

*Work in progress*

### Live Trading

I personally run this code in the cloud and can help you get started.

If you are serious about setting up my framework on a cloud server, reach out to me on [Linkedin](https://www.linkedin.com/in/dr-markus-musch-b504a21b7/).

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
