import yfinance as yf
import pandas as pd
from datetime import date

# Toggle: set to True to pull live data from Yahoo Finance via yfinance.
# Keeping this as a named constant makes it easy to find and flip if needed.
USE_REAL_DATA = True

# The four instruments we are comparing:
#   INDA  — iShares MSCI India ETF (our India proxy, USD-denominated)
#   EEM   — iShares MSCI Emerging Markets ETF (broad EM benchmark)
#   FXI   — iShares China Large-Cap ETF (China benchmark)
#   INR=X — USD/INR spot rate (pulled for reference; useful later for currency work)
TICKERS = ["INDA", "EEM", "FXI", "INR=X"]

# Start of the analysis window. 2013 is chosen because it post-dates the taper
# tantrum and aligns with the start of the Modi-era reform period.
START_DATE = "2013-01-01"


def load_data() -> pd.DataFrame:
    # Pull daily adjusted closing prices for all four tickers from Yahoo Finance.
    # auto_adjust=True tells yfinance to return prices already adjusted for
    # dividends and splits, so a dividend payout doesn't look like a price drop.
    # This matters here because INDA, EEM, and FXI pay different dividend amounts,
    # and comparing raw close prices would systematically undercount total return.

    # Set the end date to today so the window always runs to the most recent
    # available trading day.
    end_date = str(date.today())

    # Download all four tickers in a single API call. yfinance returns a
    # multi-level DataFrame; we select only the "Close" column group below.
    raw = yf.download(
        tickers=TICKERS,
        start=START_DATE,
        end=end_date,
        auto_adjust=True,
        progress=False,   # suppress the yfinance progress bar
    )

    # yfinance returns a two-level column index when multiple tickers are
    # requested: the top level is the price field (Open, High, Low, Close, Volume)
    # and the second level is the ticker. We only want "Close".
    prices = raw["Close"]

    # Drop any rows where every column is NaN. These are typically non-trading
    # days (weekends, holidays) that slipped in. We use "all" so a row is only
    # dropped if every ticker is missing — a row where just one ticker has a gap
    # is kept, because the others still have valid data.
    prices = prices.dropna(how="all")

    # Print a confirmation summary so we can verify the pull at a glance:
    # which tickers came back, the date window, and the row count.
    print(f"Tickers pulled : {list(prices.columns)}")
    print(f"Date range     : {prices.index[0].date()} → {prices.index[-1].date()}")
    print(f"Rows           : {len(prices)}")

    return prices


if __name__ == "__main__":
    df = load_data()
    print("\n--- head ---")
    print(df.head())
    print("\n--- tail ---")
    print(df.tail())
    print("\n--- shape ---")
    print(df.shape)
