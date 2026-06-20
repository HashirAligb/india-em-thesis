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


def compute_returns(prices: pd.DataFrame) -> dict:
    # Build daily percentage returns and a cumulative index (starts at 100)
    # for each ticker so we can compare growth of $100 invested on day one.

    # pct_change() computes (today - yesterday) / yesterday for every column.
    # The very first row always comes back NaN because there is no "yesterday"
    # for it. We drop that row with dropna() before doing anything else.
    #
    # Edge case we handle here: on 2013-01-01 (New Year's Day) the US equity
    # ETFs (INDA, EEM, FXI) are closed, so their price is NaN, but INR=X
    # (the forex rate) is sometimes quoted on that day. After dropna(how="all")
    # in load_data() the row survives because not ALL columns are NaN.
    # pct_change() then returns NaN for the ETFs on day 2 (can't compute a
    # return if day-1 price is NaN). We fix this by dropping any row where
    # ALL ETF columns are NaN before computing returns — INR=X is only a
    # supporting series and its holiday quirks shouldn't distort the returns.
    etf_cols = [t for t in prices.columns if t != "INR=X"]
    prices_clean = prices.dropna(subset=etf_cols, how="all")

    daily_returns = prices_clean.pct_change().dropna(how="all")

    # Cumulative index: (1 + daily_return).cumprod() gives the growth factor
    # since day one. Multiplying by 100 indexes everything to 100 at the start,
    # so the chart reads "INDA grew from 100 to X" — easy to compare across ETFs
    # even though their absolute prices differ.
    cumulative = (1 + daily_returns).cumprod() * 100

    return {"daily": daily_returns, "cumulative": cumulative}


def compute_risk_metrics(prices: pd.DataFrame) -> pd.DataFrame:
    # For each ETF compute four metrics used in the verdict:
    #   CAGR                — compound annual growth rate in USD terms
    #   Annualized Vol      — how bumpy the ride was
    #   Max Drawdown        — worst peak-to-trough loss over the full window
    #   Sharpe-style Ratio  — return per unit of risk (0% risk-free rate)
    #
    # We exclude INR=X from the metrics table because it is a currency rate,
    # not an investable asset — including it in a return/risk table would be
    # misleading. It is kept in prices for the correlation analysis.

    etf_cols = [t for t in prices.columns if t != "INR=X"]
    prices_clean = prices[etf_cols].dropna(how="all")
    daily_returns = prices_clean.pct_change().dropna(how="all")

    rows = []
    for ticker in etf_cols:
        px = prices_clean[ticker].dropna()
        ret = daily_returns[ticker].dropna()

        # CAGR: total number of calendar years in the sample, then the
        # annualisation formula (end / start) ^ (1/years) - 1.
        # We use actual calendar days so a sample that ends mid-year is not
        # over- or under-stated.
        n_years = (px.index[-1] - px.index[0]).days / 365.25
        total_return = px.iloc[-1] / px.iloc[0]
        cagr = total_return ** (1 / n_years) - 1

        # Annualized volatility: daily standard deviation scaled up by sqrt(252)
        # because there are roughly 252 trading days in a year.
        # IMPORTANT: we do NOT divide cumulative return by daily vol. That would
        # mix yearly and daily units and produce a meaningless number.
        ann_vol = ret.std() * (252 ** 0.5)

        # Max drawdown: at each point, how far below the previous peak are we?
        # cummax() tracks the running peak; dividing the price by it and
        # subtracting 1 gives the drawdown at each date. The minimum of that
        # series is the worst drawdown over the full window.
        rolling_peak = px.cummax()
        drawdown = (px / rolling_peak) - 1
        max_dd = drawdown.min()

        # Sharpe-style ratio: annualised return divided by annualised volatility.
        # Risk-free rate is set to 0% for simplicity and because we are comparing
        # across a single consistent window — the decision log documents this.
        sharpe = cagr / ann_vol if ann_vol != 0 else float("nan")

        rows.append({
            "Ticker": ticker,
            "Cumulative Return": f"{(total_return - 1) * 100:.1f}%",
            "CAGR": f"{cagr * 100:.2f}%",
            "Ann. Vol": f"{ann_vol * 100:.2f}%",
            "Max Drawdown": f"{max_dd * 100:.1f}%",
            "Sharpe-style": f"{sharpe:.3f}",
            # Store raw floats too so compute_verdict() can do comparisons
            # without re-parsing the formatted strings.
            "_cagr_raw": cagr,
            "_total_ret_raw": total_return - 1,
            "_sharpe_raw": sharpe,
        })

    return pd.DataFrame(rows)


def run_correlation_analysis(prices: pd.DataFrame) -> dict:
    # Compute rolling 12-month (252-trading-day) correlations:
    #   INDA vs EEM   — how closely India tracks broad EM
    #   INDA vs INR=X — how much of India's USD return is driven by the rupee
    #
    # Rolling correlation rather than a single number is more honest: it shows
    # whether the relationship has been stable or whether it changed over time
    # (e.g. during crises, India and EM tend to lock up together).

    # Compute returns for all tickers first (no global dropna yet).
    all_returns = prices.pct_change()

    window = 252  # approximately one trading year

    # Key fix: drop NaN per pair before rolling, not across all tickers at once.
    # INR=X is quoted on some days when US equity ETFs are closed (and vice versa),
    # so a global dropna(how="all") leaves isolated NaN holes in individual columns.
    # A single NaN anywhere in a 252-day window makes the entire window return NaN,
    # which wipes the whole series. Aligning each pair independently keeps the
    # maximum number of clean trading days for each correlation.
    pair_eem = all_returns[["INDA", "EEM"]].dropna()
    pair_inr = all_returns[["INDA", "INR=X"]].dropna()

    corr_inda_eem = (
        pair_eem["INDA"]
        .rolling(window)
        .corr(pair_eem["EEM"])
        .dropna()
    )

    corr_inda_inr = (
        pair_inr["INDA"]
        .rolling(window)
        .corr(pair_inr["INR=X"])
        .dropna()
    )

    return {"INDA_EEM": corr_inda_eem, "INDA_INR": corr_inda_inr}


def compute_verdict(metrics: pd.DataFrame) -> str:
    # Apply the pre-declared verdict rule from the thesis:
    #
    # SUPPORTED     — INDA beats BOTH EEM and FXI on cumulative return AND
    #                 on the Sharpe-style ratio.
    # PARTIALLY     — INDA beats both on return but not both risk-adjusted,
    #                 OR beats only one benchmark on both measures.
    # NOT SUPPORTED — INDA fails both benchmarks on both measures.
    #
    # We use the raw float columns (_total_ret_raw, _sharpe_raw) stored by
    # compute_risk_metrics() so we are not parsing formatted strings.

    def get(ticker, col):
        row = metrics[metrics["Ticker"] == ticker]
        return row[col].values[0]

    inda_ret = get("INDA", "_total_ret_raw")
    inda_sharpe = get("INDA", "_sharpe_raw")

    eem_ret = get("EEM", "_total_ret_raw")
    eem_sharpe = get("EEM", "_sharpe_raw")

    fxi_ret = get("FXI", "_total_ret_raw")
    fxi_sharpe = get("FXI", "_sharpe_raw")

    beats_eem_ret = inda_ret > eem_ret
    beats_fxi_ret = inda_ret > fxi_ret
    beats_eem_sharpe = inda_sharpe > eem_sharpe
    beats_fxi_sharpe = inda_sharpe > fxi_sharpe

    beats_both_ret = beats_eem_ret and beats_fxi_ret
    beats_both_sharpe = beats_eem_sharpe and beats_fxi_sharpe

    if beats_both_ret and beats_both_sharpe:
        return "SUPPORTED"
    elif beats_both_ret or beats_eem_ret or beats_fxi_ret:
        return "PARTIALLY SUPPORTED"
    else:
        return "NOT SUPPORTED"


if __name__ == "__main__":
    df = load_data()
    print("\n--- head ---")
    print(df.head())
    print("\n--- tail ---")
    print(df.tail())
    print("\n--- shape ---")
    print(df.shape)
