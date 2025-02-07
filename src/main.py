"""
Assignment:  Stock Market Analysis
Author:      Hayden Hargreaves
Date:        February 6th, 2025
Description: This program will analyze stock market data from the NASDAQ API
             and return a collection of data points for a given stock symbol.
             The program will pipe the output into a JSON file.
"""

# pylint: disable=line-too-long

from datetime import date
from typing import Any
from requests import Response, get, RequestException  # type: ignore


class Bar:
    """A class to represent a single bar of stock market data."""

    def __init__(self, data: dict):
        # For now, the date is not used.
        # self.date = data["date"]
        self.open: float = float(data["open"].replace("$", ""))
        self.high: float = float(data["high"].replace("$", ""))
        self.low: float = float(data["low"].replace("$", ""))
        self.close: float = float(data["close"].replace("$", ""))
        self.volume: int = int(data["volume"].replace(",", ""))

    def __str__(self) -> str:
        return f"Open: {self.open}, High: {self.high}, Low: {self.low}, Close: {self.close}, Volume: {self.volume}"

    def __repr__(self) -> str:
        return f"Bar({self.open}, {self.high}, {self.low}, {self.close}, {self.volume})"


class StockCollectionException(Exception):
    """An exception class for the StockData class."""


class StockData:
    """A class to represent stock market data."""

    # The number of years back to collect data from.
    years_back: int = 1

    # The number of data points to collect.
    limit: int = 10

    def construct_url(self, start: str, limit: int) -> str:
        """Create a URL to query the NASDAQ API"""
        return f"https://api.nasdaq.com/api/quote/{self.symbol.upper()}/historical?assetclass=stocks&fromdate={start}&limit={limit}"

    def get_ticker_data(self) -> Any:
        """
        Get stock market data for a given symbol. A user agent must be provided
        otherwise the API will hangup. I provided my user agent from my desktop.
        """
        try:
            start: str = str(
                date.today().replace(year=date.today().year - self.years_back)
            )
            data: Response = get(
                self.construct_url(start, self.limit),
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code != 200:
                self.error = f"Error: {data.status_code} - {data.reason}"
                return None

            return data.json()["data"]["tradesTable"]["rows"]

        # There are far too many exceptions to catch, so I'm just going to catch all
        except RequestException as e:
            self.error = f"Error: {e}"
            return None

    def process_data(self) -> None:
        """Process the data collected from the API."""
        for _bar in self.bars:
            b = Bar(_bar)
            print(b)

    def __str__(self) -> str:
        """String representation of the class."""
        return f"{self.bars}"

    def __init__(self, symbol: str):
        """Create a new stock data object."""
        self.symbol = symbol
        self.error = ""
        self.bars = self.get_ticker_data()

        if self.error != "" or self.bars is None:
            raise StockCollectionException(self.error)


if __name__ == "__main__":
    aapl = StockData("AAPL")
    aapl.process_data()
