"""Live news and market data to supplement snapshot context for chat."""

from __future__ import annotations

import asyncio
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

_HTML_TAG_RE = re.compile(r"<[^>]+>")

import feedparser
import httpx

from backend.ingestion.cache import read_latest_cache
from backend.settings import settings

_USER_AGENT = "MarutiSupplyChainCommandCenter/1.0 (demo; +https://localhost)"
_YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
_GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

_DEFAULT_NEWS_QUERIES = [
    "Maruti Suzuki supply chain India",
    "MRF tyres automotive India",
    "Red Sea shipping rubber automotive",
]

_TIRE_NEWS_QUERIES = [
    "MRF tyres India OEM automotive",
    "Gulf petrochemical synthetic rubber supply",
    "India tyre industry Red Sea shipping",
]


def _news_queries_for_message(user_message: str, snapshot: dict[str, Any] | None) -> list[str]:
    msg = user_message.lower()
    if any(k in msg for k in ("mrf", "tyre", "tire", "gulf", "rubber", "red sea", "carbon black")):
        return _TIRE_NEWS_QUERIES
    if snapshot and snapshot.get("tire_disruption_brief"):
        return _DEFAULT_NEWS_QUERIES
    if any(k in msg for k in ("maruti", "supplier", "semiconductor", "chip", "risk")):
        return _DEFAULT_NEWS_QUERIES[:2]
    return _DEFAULT_NEWS_QUERIES[:1]


def _yahoo_symbols_for_message(user_message: str) -> list[str]:
    msg = user_message.lower()
    symbols: list[str] = []
    if any(k in msg for k in ("mrf", "tyre", "tire", "rubber")) or "supplier" in msg:
        symbols.append("MRF.NS")
    if any(
        k in msg
        for k in ("maruti", "msil", "oem", "stock", "share", "nse", "market", "finance")
    ):
        symbols.append("MARUTI.NS")
    if not symbols and ("risk" in msg or "fear" in msg or "greed" in msg):
        symbols.extend(["MRF.NS", "MARUTI.NS"])
    return list(dict.fromkeys(symbols))


def _strip_html(text: str) -> str:
    return _HTML_TAG_RE.sub("", text).replace("&nbsp;", " ").strip()


def _parse_google_news_rss(url: str, limit: int) -> list[dict[str, str]]:
    parsed = feedparser.parse(url, agent=_USER_AGENT)
    out: list[dict[str, str]] = []
    for entry in parsed.entries[:limit]:
        out.append(
            {
                "title": _strip_html(entry.get("title") or "")[:200],
                "summary": _strip_html(
                    entry.get("summary") or entry.get("description") or ""
                )[:320],
                "url": entry.get("link") or "",
                "source": "google_news_rss",
            }
        )
    return out


async def _fetch_google_news(query: str, limit: int = 4) -> list[dict[str, str]]:
    url = _GOOGLE_NEWS_RSS.format(query=urllib.parse.quote(query))
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_parse_google_news_rss, url, limit),
            timeout=8.0,
        )
    except (asyncio.TimeoutError, Exception):
        return []


async def _fetch_yahoo_quote(symbol: str) -> dict[str, Any] | None:
    headers = {"User-Agent": _USER_AGENT}
    params = {"interval": "1d", "range": "5d"}
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            r = await client.get(_YAHOO_CHART.format(symbol=symbol), params=params)
            r.raise_for_status()
            data = r.json()
        result = (data.get("chart") or {}).get("result") or []
        if not result:
            return None
        meta = result[0].get("meta") or {}
        closes = (result[0].get("indicators") or {}).get("quote", [{}])
        close_series = (closes[0].get("close") if closes else None) or []
        valid = [c for c in close_series if c is not None]
        change_pct = None
        if len(valid) >= 2 and valid[-2]:
            change_pct = ((valid[-1] - valid[-2]) / valid[-2]) * 100
        return {
            "symbol": symbol,
            "currency": meta.get("currency", "INR"),
            "exchange": meta.get("exchangeName", ""),
            "price": meta.get("regularMarketPrice"),
            "previous_close": meta.get("chartPreviousClose") or meta.get("previousClose"),
            "change_pct_1d": round(change_pct, 2) if change_pct is not None else None,
            "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
    except Exception:
        return None


def _cached_rss_headlines(keywords: tuple[str, ...], limit: int = 5) -> list[str]:
    cached = read_latest_cache("rss")
    if not cached:
        return []
    articles = cached.get("articles") or []
    lines: list[str] = []
    for art in articles:
        blob = f"{art.get('title', '')} {art.get('summary', '')}".lower()
        if keywords and not any(k in blob for k in keywords):
            continue
        lines.append(f"- {art.get('title', '')[:120]}")
        if len(lines) >= limit:
            break
    return lines


async def build_live_enrichment(
    user_message: str,
    snapshot: dict[str, Any] | None,
    *,
    timeout_seconds: float | None = None,
) -> str:
    """Fetch Google News RSS + Yahoo Finance + cached RSS for the chat system prompt."""
    timeout = timeout_seconds or settings.chat_enrichment_timeout_seconds
    lines: list[str] = [
        "LIVE ENRICHMENT (open web — supplement analysis snapshot; cite when relevant):"
    ]

    queries = _news_queries_for_message(user_message, snapshot)
    symbols = _yahoo_symbols_for_message(user_message)

    news_tasks = [_fetch_google_news(q, limit=3) for q in queries[:3]]
    yahoo_tasks = [_fetch_yahoo_quote(s) for s in symbols[:3]]

    try:
        results = await asyncio.wait_for(
            asyncio.gather(*news_tasks, *yahoo_tasks, return_exceptions=True),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        lines.append("- Live fetch timed out; use snapshot data only.")
        return "\n".join(lines)

    seen_titles: set[str] = set()
    news_idx = 0
    for batch in results[: len(news_tasks)]:
        if isinstance(batch, Exception) or not batch:
            continue
        q = queries[news_idx] if news_idx < len(queries) else "news"
        news_idx += 1
        for item in batch:
            title = item.get("title", "")
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            summary = item.get("summary", "").replace("\n", " ")[:180]
            lines.append(f'- Google News (“{q[:40]}”): {title} — {summary}')

    for batch in results[len(news_tasks) :]:
        if isinstance(batch, Exception) or not batch:
            continue
        sym = batch.get("symbol", "")
        price = batch.get("price")
        chg = batch.get("change_pct_1d")
        chg_s = f", 1d change {chg:+.2f}%" if chg is not None else ""
        if price is not None:
            lines.append(
                f"- Yahoo Finance {sym}: ₹{price:.2f} {batch.get('currency', 'INR')}{chg_s} "
                f"({batch.get('as_of', '')})"
            )

    kw = ("mrf", "tyre", "tire", "rubber", "gulf", "maruti", "supply")
    if any(k in user_message.lower() for k in kw):
        cached_lines = _cached_rss_headlines(kw, limit=4)
    else:
        cached_lines = _cached_rss_headlines(("supply", "auto", "maruti"), limit=3)
    if cached_lines:
        lines.append("Cached RSS ingest (from last Run analysis):")
        lines.extend(cached_lines)

    if len(lines) == 1:
        lines.append("- No live headlines retrieved; rely on snapshot CONTEXT.")
    return "\n".join(lines)
