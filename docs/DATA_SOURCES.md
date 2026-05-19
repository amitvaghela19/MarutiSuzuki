# Data sources

## Tier 0 (no API key)

| Provider | Fallback |
|----------|----------|
| World Bank v2 | Demo macro series if API fails |
| GDELT DOC 2.0 | RSS + cache if throttled |
| RSS feeds | Demo headline if parse fails |

## Tier 1 (optional)

| Provider | Env var |
|----------|---------|
| FRED | `FRED_API_KEY` |
| NewsData.io | `NEWSDATA_API_KEY` |

## Cache layout

`data/cache/{provider}/{date}.json` — analysis uses latest cache when live fetch is stale.
