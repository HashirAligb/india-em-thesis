"""
World Bank API refresh functions.

Pipeline: data_engine -> layer2 -> assumption_audit -> verdict_agents -> app.
Optional side input to the Layer 2 step: the Part 2 refresh buttons in app.py
call these to swap pinned WGI and Findex data for live values. The declared
verdict and the Assumption Auditor always use the pinned data.

Pulls live WGI and Findex data and returns dicts in the same shape
that app.py and the scoring functions consume.

Both public functions return None on any error (network, timeout, shape
mismatch) so callers can fall back to the pinned dataset without
breaking the page.

Endpoints:
  WGI   - http://api.worldbank.org/v2/country/{iso}/indicator/{code}
           Indicators: GOV_WGI_{CC|GE|PV|RL|RQ|VA}.EST  (source=3)
  Findex - http://api.worldbank.org/v2/country/{iso}/indicator/{code}
           Indicators: g20.any, merchant.pay  (source=28)

HTTPS times out in some environments; the module uses plain HTTP throughout.
"""

import json
import datetime
import statistics
import urllib.request
import urllib.error
from typing import Optional

_BASE    = "http://api.worldbank.org/v2"
_TIMEOUT = 12  # seconds per request
_HEADERS = {"User-Agent": "India-EM-Thesis-Refresh/1.0"}

# WGI indicator codes in the same order as the pinned wgi_table.dimensions list.
_WGI_CODES = [
    ("GOV_WGI_VA.EST", "Voice and Accountability"),
    ("GOV_WGI_PV.EST", "Political Stability and Abs. of Violence"),
    ("GOV_WGI_GE.EST", "Government Effectiveness"),
    ("GOV_WGI_RQ.EST", "Regulatory Quality"),
    ("GOV_WGI_RL.EST", "Rule of Law"),
    ("GOV_WGI_CC.EST", "Control of Corruption"),
]
_WGI_YEARS = [2014, 2019, 2023]

# Findex peer set: same 10 countries as the pinned peer_table_2024.
_FINDEX_SOURCE          = 28
_FINDEX_COUNTRY_PARAM   = "IN;CN;ID;BR;MX;ZA;TR;TH;MY;PH"
_FINDEX_ISO3_TO_NAME    = {
    "IND": "India",
    "CHN": "China",
    "IDN": "Indonesia",
    "BRA": "Brazil",
    "MEX": "Mexico",
    "ZAF": "South Africa",
    "TUR": "Turkey",
    "THA": "Thailand",
    "MYS": "Malaysia",
    "PHL": "Philippines",
}


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get(url: str) -> list:
    """Fetch one World Bank API URL and return its data rows (the second item of the reply).
    Raises on any problem so each fetch_* function needs only one try/except.
    Called by fetch_wgi() and fetch_findex()."""
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        raw = json.loads(resp.read().decode())
    if isinstance(raw, dict):
        msg = (raw.get("message") or [{}])[0].get("value", "unknown WB API error")
        raise ValueError(f"WB API error: {msg}")
    if len(raw) < 2 or not raw[1]:
        raise ValueError("WB API returned empty data list")
    return raw[1]


# ── Public refresh functions ──────────────────────────────────────────────────

def fetch_wgi() -> Optional[dict]:
    """Live WGI scores for India and China (2014, 2019, 2023), shaped like the pinned JSON table.
    Matching the pinned shape means scoring can't tell live from pinned; returns None on any failure.
    Called by the WGI refresh button in app.py (Part 2) via _do_refresh_wgi()."""
    try:
        dimensions = []
        for code, dim_name in _WGI_CODES:
            url = (
                f"{_BASE}/country/IN;CN/indicator/{code}"
                f"?format=json"
                f"&date={min(_WGI_YEARS)}:{max(_WGI_YEARS)}"
                f"&per_page=50"
            )
            rows = _get(url)
            india: dict = {}
            china: dict = {}
            for row in rows:
                iso3 = row.get("countryiso3code", "")
                year = int(row["date"])
                val  = row["value"]
                if val is None or year not in _WGI_YEARS:
                    continue
                if iso3 == "IND":
                    india[str(year)] = round(float(val), 2)
                elif iso3 == "CHN":
                    china[str(year)] = round(float(val), 2)

            # Require all three years for both countries.
            required = {str(y) for y in _WGI_YEARS}
            if not (required <= india.keys() and required <= china.keys()):
                raise ValueError(
                    f"Incomplete WGI data for {dim_name}: "
                    f"india={list(india)}, china={list(china)}"
                )
            dimensions.append({"name": dim_name, "india": india, "china": china})

        return {
            "dimensions":   dimensions,
            "fetched_at":   _utc_now(),
            "latest_year":  max(_WGI_YEARS),
        }

    except Exception:
        return None


def fetch_findex() -> Optional[dict]:
    """Live Findex digital payment rates for India and nine EM peers, plus the peer medians.
    Shaped like the pinned peer table; returns None on any failure so the page falls back to pinned.
    Called by the Findex refresh button in app.py (Part 2) via _do_refresh_findex()."""
    try:
        def _findex_url(indicator: str) -> str:
            """Build the Findex API URL for one indicator code."""
            return (
                f"{_BASE}/country/{_FINDEX_COUNTRY_PARAM}/indicator/{indicator}"
                f"?source={_FINDEX_SOURCE}&format=json&per_page=20&mrv=1"
            )

        any_rows     = _get(_findex_url("g20.any"))
        merchant_rows = _get(_findex_url("merchant.pay"))

        data_year = int(any_rows[0]["date"]) if any_rows else 2024

        # Findex leaves countryiso3code empty; country.id carries the ISO3 code.
        any_vals   = {r["country"]["id"]: float(r["value"])
                      for r in any_rows if r["value"] is not None}
        merch_vals = {r["country"]["id"]: float(r["value"])
                      for r in merchant_rows if r["value"] is not None}

        india_any   = any_vals.get("IND")
        india_merch = merch_vals.get("IND")
        if india_any is None or india_merch is None:
            raise ValueError("India data missing from Findex response")

        # Peer median excludes India.
        peer_any_vals   = [v for iso, v in any_vals.items()  if iso != "IND"]
        peer_merch_vals = [v for iso, v in merch_vals.items() if iso != "IND"]
        if not peer_any_vals:
            raise ValueError("No peer data in Findex response")

        peer_median_any   = statistics.median(peer_any_vals)
        peer_median_merch = statistics.median(peer_merch_vals)

        # Build peer table in the same shape as peer_table_2024.
        peer_table = []
        for iso3, name in _FINDEX_ISO3_TO_NAME.items():
            a = any_vals.get(iso3)
            m = merch_vals.get(iso3)
            if a is not None and m is not None:
                peer_table.append({
                    "country":      name,
                    "any_pct":      round(a, 1),
                    "merchant_pct": round(m, 1),
                })
        peer_table.sort(key=lambda r: r["country"])

        return {
            "india_any":             round(india_any, 1),
            "peer_median_any":       round(peer_median_any, 1),
            "india_merchant":        round(india_merch, 1),
            "peer_median_merchant":  round(peer_median_merch, 1),
            "peer_table":            peer_table,
            "data_year":             data_year,
            "fetched_at":            _utc_now(),
        }

    except Exception:
        return None


# ── Utility ───────────────────────────────────────────────────────────────────

def _utc_now() -> str:
    """Current UTC time as text like "2026-10-29T12:00:00Z", for the fetched_at stamp."""
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
