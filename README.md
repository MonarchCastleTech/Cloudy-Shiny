<div align="center">
  <img src="logo.png" alt="Cloudy&amp;Shiny Index logo" width="420">

  # Cloudy&Shiny Index
  ### Hourly global fear &amp; greed market-sentiment dashboard

  <!-- badge row -->
  ![status](https://img.shields.io/badge/status-active-brightgreen)
  ![division](https://img.shields.io/badge/Financial%20Intelligence-0b1f3a)
  ![Monarch Castle](https://img.shields.io/badge/Monarch%20Castle-Holdings-1f6feb)
  ![license](https://img.shields.io/badge/license-see%20LICENSE-lightgrey)
</div>

> **Executive summary** — Cloudy Shiny is a self-refreshing market-sentiment terminal that condenses equities, crypto, and volatility signals into a single, decision-grade **Cloudy&Shiny Index** (0–100). It serves analysts, traders, and decision-makers who need a fast, defensible read on global risk appetite without staring at a dozen feeds. Every reading is timestamped, provenance-logged, and rebuilt automatically on an hourly cadence, then published as a static dashboard on GitHub Pages.

## ✨ Highlights
- **Composite Cloudy&Shiny Index (0–100)** blending stock momentum, crypto fear/greed, and inverted volatility into one read, classified into **STORMY** (extreme fear), **CLOUDY** (neutral), and **SHINY** (extreme greed) regimes.
- **Three independent live inputs** — equity-momentum scoring (SPY/QQQ), the crypto Fear &amp; Greed Index, and the CBOE VIX — each normalised to a common 0–100 scale before weighting.
- **Global market-breadth panel** spanning 12 instruments across the US, Europe, and Asia (S&amp;P 500, Nasdaq 100, DAX, CAC 40, Nikkei 225, Shanghai Composite, Hang Seng, BIST 100) plus the classic "fear" assets (VIX, US 20Y Treasuries, Gold, US Dollar Index).
- **Quantitative forecast layer** — an ensemble of AR(1), damped-trend regression, and EWMA mean-reversion models projects the index forward and assigns regime probabilities.
- **Feed-health telemetry** — every refresh records per-source status, latency, and fallback usage to `feed_health.csv`, so stale or degraded inputs are visible, not hidden.
- **Graceful degradation** — the pipeline falls back to the last good values on partial outages and never crashes the dashboard on a single failed feed.
- **Fully automated** — a GitHub Actions cron workflow refreshes the data, rebuilds the static `index.html`, and publishes to GitHub Pages on an hourly cadence with retry and concurrency guards.

## 🖼️ Preview
<!-- CODEX: drop product screenshots into docs/ -->
<!-- ![Cloudy Shiny — main view](docs/screenshot-1.png) (screenshot pending) -->
<!-- CODEX: capture the live dashboard at https://monarchcastletech.github.io/Cloudy-Shiny/ — the hero view showing the Cloudy&Shiny Index half-circle gauge, the composite score, and the STORMY/CLOUDY/SHINY regime label. Terminal-style dark theme. -->

<!-- ![Cloudy Shiny — global breadth &amp; forecast detail](docs/screenshot-2.png) (screenshot pending) -->
<!-- CODEX: capture the lower panels — the 12-instrument global market-breadth grid and the quant forecast / regime-probability section. -->

## 🧭 What it does
Cloudy Shiny turns a handful of market feeds into a single, legible sentiment signal and a supporting analytics terminal.

### The Cloudy&Shiny Index
The headline number is a weighted composite computed each refresh:

```
index = (stock × 0.4) + (crypto × 0.3) + ((100 − vix_normalized) × 0.3)
```

- **Stock sentiment (40%)** — derived from SPY (0.6) and QQQ (0.4) via 50-day moving-average deviation, with an RSI(14) overbought/oversold adjustment, clamped to 0–100.
- **Crypto sentiment (30%)** — the alternative.me Crypto Fear &amp; Greed Index, used directly on its native 0–100 scale.
- **Volatility (30%)** — the CBOE VIX, normalised against its trailing one-year range and **inverted**, so calm markets push the index up and spikes pull it down.

The resulting score maps to a regime band: **STORMY** (≤ 20), **CLOUDY** (21–80), **SHINY** (> 80).

### Global market breadth
Beyond the headline index, the dashboard renders a GDP-weighted view of 12 instruments across the US, Europe, and Asia, separating "risk-on" indices from "risk-off" assets (VIX, long Treasuries, Gold, the Dollar Index) to show where global appetite is concentrated.

### Forecast &amp; regime probabilities
A lightweight quant layer projects the index forward using an ensemble of three models — an AR(1) autoregression, a damped local-trend regression, and an EWMA mean-reversion estimate — and converts the projected distribution into STORMY / CLOUDY / SHINY probabilities via a normal-CDF regime model.

## 🗂️ Data &amp; provenance
Per Monarch Castle doctrine — **evidence before assertion**. Cloudy Shiny collects only from open, lawfully accessible market sources and records the trail for every reading.

| Source | Provider | Access | Cadence |
|---|---|---|---|
| Equity prices (SPY, QQQ, global indices) | Yahoo Finance via `yfinance` | Public market data | Hourly |
| Crypto Fear &amp; Greed Index | alternative.me (`api.alternative.me/fng`) | Public JSON API | Hourly |
| Volatility (VIX) | Yahoo Finance via `yfinance` (`^VIX`) | Public market data | Hourly |

- **`sentiment_data.csv`** is the historical store — one timestamped row per refresh carrying the raw stock, crypto, VIX, and normalised VIX inputs alongside the computed `mood_score` and `mood_label`.
- **`feed_health.csv`** is the provenance/audit log — per-source status (`live` / `fallback` / `failed` / `missing`), per-source latency in milliseconds, whether a fallback was used, and any error notes, all UTC-timestamped.
- Network calls use bounded timeouts and retry-with-backoff; on failure the pipeline reuses the last known values and flags the substitution rather than emitting an un-provenanced number.

## 🛠️ Tech stack
- **Language:** Python 3.11
- **Data &amp; analytics:** `pandas`, `yfinance`, `requests`
- **Visualisation:** static HTML/SVG terminal template (`template.html` → `index.html`), with `plotly` available for charting
- **Interactive app:** `streamlit` (`app.py`) for local exploration
- **Automation:** GitHub Actions (scheduled cron) — `.github/workflows/hourly.yml`
- **Hosting:** GitHub Pages (static `index.html`)

## 🚀 Getting started

**Live dashboard:** https://monarchcastletech.github.io/Cloudy-Shiny/

### Run locally
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Fetch the latest sentiment reading (writes sentiment_data.csv + feed_health.csv)
python sentiment_tracker.py

# 3a. Build the static dashboard (writes index.html)
python build_index.py
# open index.html in a browser

# 3b. …or run the interactive Streamlit terminal
streamlit run app.py
```
On Windows, `open_system.bat` provides a one-click launch wrapper.

### Automated refresh
`.github/workflows/hourly.yml` runs on a scheduled cron (~50-minute cadence) plus manual `workflow_dispatch`. Scheduled and live manual runs fetch fresh data, rebuild `index.html`, and commit the updated `index.html`, `sentiment_data.csv`, and `feed_health.csv` back to the branch — with retry logic and a concurrency guard so runs never collide. Manual dispatch defaults to a safe dry-run that validates the committed dashboard without fetching or publishing. GitHub Pages serves the committed `index.html` directly.

## 🧱 Part of Monarch Castle
> A product of **Financial Intelligence** · **Monarch Castle Technologies** — an operating company of **[Monarch Castle Holdings](https://github.com/MonarchCastleHoldings)**.
> Sister companies: [Monarch Castle Technologies](https://github.com/monarchcastletech) · [Strategic Data Company of Ankara](https://github.com/SDCofA)

## 📜 License
See `LICENSE`. © 2026 Monarch Castle Holdings · Ankara, Türkiye.

<div align="center"><sub>🏰 Monarch Castle Holdings — turning open-source noise into lawful, verified, decision-grade intelligence.</sub></div>

---

<!-- repository-hygiene:start -->

![Monarch Castle Technologies approved lockup](docs/brand/organization-lockup.png)

Hourly global fear & greed market-sentiment dashboard — the Cloudy&Shiny Index. Financial Intelligence, Monarch Castle Technologies.

![Lifecycle: Active](docs/lifecycle-active.svg)

## Repository status

Lifecycle: **Active**. The badge and this statement describe maintenance status, not service availability.

## Public access

[Open the published project](https://monarchcastletech.github.io/Cloudy-Shiny/)

## Screenshots

![Cloudy&Shiny Index repository preview](docs/social-preview.png)

The preview is maintained as a repository asset; the live interface or generated output remains authoritative.

## Data and methodology

- [sentiment_tracker.py](sentiment_tracker.py)
- [feed_health.csv](feed_health.csv)

These repository-specific sources define the methodology or provenance boundary. Source dates, transformation steps, and known gaps must travel with analytical outputs.

## Update frequency

The published sentiment pipeline targets hourly refreshes; feed-health records expose missed or degraded inputs.

## Quick start

```shell
python -m pip install -r requirements.txt
```

```shell
streamlit run app.py
```

Run only in a trusted development environment and review repository-specific prerequisites before using networked or hardware features.

## Architecture

- `app.py` — repository-specific implementation, data, or configuration boundary.
- `sentiment_tracker.py` — repository-specific implementation, data, or configuration boundary.

## Tests

```shell
python -m unittest discover -v
```

```shell
node --test tests/repository-hygiene.test.mjs
```

## Provenance

Original software history is maintained in Git. External datasets, reports, trademarks, screenshots, and assets are not relicensed by this repository; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before reuse.

## Forecast limitations

Forecasts and model-derived scores are probabilistic, time-bound analytical outputs—not facts, guarantees, or advice. Evaluate them against their stated horizon, source timestamp, methodology, and subsequent outcomes. Missing or delayed inputs can defer publication.

## Security

Do not publish vulnerabilities in an issue. Use GitHub's private vulnerability-reporting flow when available, or follow the [organization security policy](https://github.com/MonarchCastleTech/.github/security/policy).

## License

Original repository code and documentation are available under **MIT**; see [LICENSE](LICENSE). That license does not override third-party terms documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Citation

Use the machine-readable [CITATION.cff](CITATION.cff). Cite the specific commit and, for analytical use, record the data or model snapshot date.

## Masterbrand endorsement

Cloudy&Shiny Index is a Monarch Castle Technologies project. **Part of Monarch Castle Technologies.**

<!-- repository-hygiene:end -->
