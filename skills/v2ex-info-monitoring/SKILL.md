---
name: v2ex-info-monitoring
description: Monitor info.v2ex.pro using its underlying GitHub daily dataset instead of brittle page scraping. Fetch weekly price/AAM/Livid signals, detect anomalies, and drive quiet-only-on-exception alerts.
version: 1.0.0
author: Hermes Agent
---

# V2EX Info Monitoring

Use this when the user wants tracking or alerts for `https://info.v2ex.pro/`, especially:
- price
- AAM inventory / `main_amm_v2ex_amount`
- `livid` holdings / address changes
- weekly anomaly-only alerts instead of noisy daily summaries

## Key finding

Do not start with page scraping. `info.v2ex.pro` is easier to monitor through the backing GitHub dataset:
- repo: `GrabCoffee/v2ex-info-newsletter-data`
- raw base: `https://raw.githubusercontent.com/GrabCoffee/v2ex-info-newsletter-data/master/daily/{date}/{filename}`

This is more stable and script-friendly than trying to infer structure from the rendered site.

Useful files per day:
- `hodl_snapshots.json` → end-of-day price and AAM snapshots
- `top50_address_changes.json` → address-level holding changes; use this to detect `livid`

## Recommended workflow

1. Determine the lookback window first (default: 7 days for anomaly checks).
2. Pull daily raw JSON files from GitHub, not the webpage.
3. Build a compact time series with:
   - `price_close`
   - `aam_close`
   - latest `livid` holding snapshot if present
   - `livid` amount delta / rank delta if present
4. Detect anomalies from day-over-day change.
5. Keep a local state file so repeated runs only alert on new anomalies.
6. For cron jobs, inject the script's compact JSON output into the prompt and tell the model to use that as the only data source.

## Suggested anomaly rules

These worked well as a first-pass weekly monitor:
- `PRICE_ALERT_PCT = 8.0`
- `AAM_ALERT_PCT = 4.0`
- `LIVID_ALERT_AMOUNT = 50000.0`
- `LIVID_ALERT_RANK = 5`

Also treat data quality issues as alertable events when appropriate:
- if the latest day's price and AAM are both missing/zero, mark it as a likely source collection issue rather than a real market move

## Important pitfalls

- The newest day can contain zeros / missing values. Do not automatically interpret that as a crash.
- Explicitly label all-zero latest-day data as `采集异常/数据源异常` unless corroborated elsewhere.
- `livid` may not appear every day in the top-50 changes dataset. Missing does not necessarily mean holdings went to zero.
- Some site navigation/browser clicks may time out; browser probing is fine for reconnaissance, but production monitoring should rely on the GitHub raw files.

## Alerting style

Prefer anomaly-driven alerts, not routine spam.

Good pattern:
- cron pre-script computes `series`, `anomalies`, `should_alert`
- prompt says: if `should_alert` is false, do not send a user-facing message
- if true, send a concise Chinese summary with clear distinction between:
  - real candidate market moves
  - data-source / collection anomalies

Useful emojis:
- `📈` upward move
- `📉` downward move
- `⚠️` anomaly / data issue
- `💤` no meaningful change

## Example fields to emit from the pre-script

```json
{
  "lookback_days": 7,
  "series": [],
  "anomalies": [],
  "should_alert": true,
  "notes": [
    "If latest price/AAM are all zero, treat as likely source anomaly."
  ]
}
```

## When this skill is a better choice than RSS

The site may expose an RSS feed, but for structured monitoring of numeric fields, prefer the GitHub daily JSON source. RSS is fine for human-readable newsletters; it is not the best primary source for numeric anomaly detection.
