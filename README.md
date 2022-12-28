
# Trading Bot

**One-stop toolkit for fully automated algorithmic trading.**

### Includes:

1. Data Handling

	* A DataHandler class that serves as a processing interface between a REST client handling communication with different APIs and your csv data with a unified structure.
    * A datapipline module that can easily be adapted to fetch data of your favorite coin and time frame and store it into a csv file.
	* A collection of csv files with the data of your favorite coins to improve backtesting speed and enable coding work offline.

2. Backtesting

	* A Backtest class serving as a template for backtesting any strategy you will implement.
	* Two backtest modules for an example strategy and an example portfolio that you can copy paste and easily adapt to your use case.
	* Backtest reports for the example strategy including plots of the equity curve and important performance metrics for different parameters.

    [Image](./images/portfolio_equity_curve.png) 

3. Live Trading

	* A REST client to deal with Binance API that you can easily adapt to work with your favorite exchanges' REST APIs.
	* An abstract Strategy class that serves as a template for implementing your own strategies.
	* An example strategy that serves as a blueprint for your own strategies or as a starting point to build upon.
	* A Portfolio class that makes combining your strategies into full portfolios straight forward.

## Installation

All third party modules are listed in the [requirements](requirements.txt) file.

Run 'pip install -r requirements.txt' to fetch them all at once.

## Usage

### Getting Data

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