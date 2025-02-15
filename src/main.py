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
import json
from typing import Any, List
import sys
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
    years_back: int = 5

    # The number of data points to collect.
    limit: int = 5

    def construct_url(self, start: str, limit: int) -> str:
        """Create a URL to query the NASDAQ API"""
        return f"https://api.nasdaq.com/api/quote/{self.symbol.upper()}/historical?assetclass=stocks&fromdate={start}&limit={limit}"

    def get_ticker_data(self) -> List[Bar]:
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
            if data.status_code != 200 or data.json()["data"] is None:
                self.error = f"Error: {data.json()["status"]["rCode"]}: {data.json()["status"]["bCodeMessage"][0]["errorMessage"]} ({self.symbol})"
                return []

            if data.json()["data"]["tradesTable"]["rows"] is None:
                self.error = f"Error: No data found for {self.symbol}"
                return []

            bars: List[Bar] = [
                Bar(_bar) for _bar in data.json()["data"]["tradesTable"]["rows"]
            ]
            self.min = round(min(_bar.close for _bar in bars), 2)
            self.max = round(max(_bar.close for _bar in bars), 2)
            self.avg = round(sum(_bar.close for _bar in bars) / len(bars), 2)
            self.median = round(sorted(_bar.close for _bar in bars)[len(bars) // 2], 2)
            return bars

        # There are far too many exceptions to catch, so I'm just going to catch all
        except RequestException as e:
            self.error = f"Error: {e}"
            return []

    def get_data(self) -> dict[str, Any]:
        """Return the data points as a dictionary."""
        return {
            "symbol": self.symbol,
            "max": self.max,
            "min": self.min,
            "avg": self.avg,
            "median": self.median,
        }

    def __str__(self) -> str:
        """Return a string representation of the stock data."""
        return f"Symbol: {self.symbol}, Min: {self.min}, Max: {self.max}, Avg: {self.avg}, Median: {self.median}"

    def __init__(self, symbol: str):
        """Create a new stock data object."""
        self.symbol = symbol
        self.error = ""

        self.min, self.max, self.avg, self.median = (0, 0, 0, 0)
        self.__bars = self.get_ticker_data()

        if self.error != "" or self.__bars is None:
            raise StockCollectionException(self.error)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py [symbol...]")
        sys.exit(1)

    results: List[dict] = []
    for arg in sys.argv[1:]:
        try:
            s = StockData(arg.upper())
            results.append(s.get_data())
        except StockCollectionException as e:
            results.append({"symbol": arg.upper(), "error": str(e)})
            print(e)

    try:
        with open("stock.json", "w", encoding="UTF-8") as file:
            file.write(json.dumps(results, indent=2))
    except IOError as e:
        print("Failed to write to file. {e}")
