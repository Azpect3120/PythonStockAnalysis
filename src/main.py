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
from requests import Response, get  # type: ignore

YEARS_BACK: int = 1


def construct_url(symbol: str, start: str, limit: int) -> str:
    """Create a URL to query the NASDAQ API"""
    url: str = "https://api.nasdaq.com"
    url += f"/api/quote/{symbol.upper()}/historical"
    url += f"?assetclass=stocks&fromdate={start}&limit={limit}"
    return url


def get_ticker_data(symbol: str) -> None:
    """
    Get stock market data for a given symbol. A user agent must be provided
    otherwise the API will hangup. I provided my user agent from my desktop.
    """
    try:
        start: str = str(date.today().replace(year=date.today().year - YEARS_BACK))
        data: Response = get(
            construct_url(symbol, start, 9999),
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
                "Content-Type": "application/json",
            },
        )
        if data.status_code == 200:
            print(data.json())
        else:
            print(f"Error: {data.status_code}")

    # There are far too many exceptions to catch, so I'm just going to catch all
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    get_ticker_data("AAPL")
