import json
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

import duckdb

from backend.db.migrate import migrate
from backend.ingestion.dates import parse_published_at
from backend.settings import settings


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@contextmanager
def get_conn() -> Iterator[duckdb.DuckDBPyConnection]:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(settings.db_path))
    try:
        migrate(conn)
        yield conn
        conn.commit()
    finally:
        conn.close()


class Repository:
    def upsert_health(
        self,
        provider: str,
        *,
        ok: bool,
        error: str | None = None,
        latency_ms: int | None = None,
    ) -> None:
        status = "ok" if ok else "stale"
        now = _utcnow()
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO data_source_health (provider, last_ok, last_error, latency_ms, status)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (provider) DO UPDATE SET
                    last_ok = CASE WHEN excluded.status = 'ok' THEN excluded.last_ok ELSE data_source_health.last_ok END,
                    last_error = excluded.last_error,
                    latency_ms = excluded.latency_ms,
                    status = excluded.status
                """,
                [provider, now if ok else None, error, latency_ms, status],
            )

    def start_run(self, run_id: str) -> None:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO analysis_runs (run_id, started_at) VALUES (?, ?)",
                [run_id, _utcnow()],
            )

    def finish_run(self, run_id: str, data_health: dict[str, Any]) -> None:
        with get_conn() as conn:
            conn.execute(
                "UPDATE analysis_runs SET finished_at = ?, data_health_json = ? WHERE run_id = ?",
                [_utcnow(), json.dumps(data_health), run_id],
            )

    def sync_config_entities(self, cfg: Any) -> None:
        with get_conn() as conn:
            for c in cfg.data_sources.countries:
                conn.execute(
                    "INSERT OR REPLACE INTO countries (code, name) VALUES (?, ?)",
                    [c.code, c.name],
                )
            for s in cfg.suppliers:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO suppliers
                    (id, name, country_code, commodities_json, cost_index, lead_time_days, capability_flags_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        s.id,
                        s.name,
                        s.country,
                        json.dumps(s.commodities),
                        s.cost_index,
                        s.lead_time_days,
                        json.dumps(s.capability_flags),
                    ],
                )
            for p in cfg.parts:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO parts (id, name, criticality, main_commodity, supplier_ids_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [p.id, p.name, p.criticality, p.main_commodity, json.dumps(p.supplier_ids)],
                )
            for pl in cfg.plants:
                conn.execute(
                    "INSERT OR REPLACE INTO plants (id, name, location, parts_used_json) VALUES (?, ?, ?, ?)",
                    [pl.id, pl.name, pl.location, json.dumps(pl.parts_used)],
                )
            for com in cfg.data_sources.commodity_series:
                conn.execute(
                    "INSERT OR REPLACE INTO commodities (id, name, unit) VALUES (?, ?, ?)",
                    [com.id, com.name, com.unit or ""],
                )
            for sc in cfg.scenarios:
                conn.execute(
                    "INSERT OR REPLACE INTO scenarios (id, name, description, shock_json) VALUES (?, ?, ?, ?)",
                    [sc.id, sc.name, sc.description, json.dumps(sc.shock)],
                )

    def bulk_insert_risks(
        self,
        run_id: str,
        table: str,
        rows: list[tuple[str, float, dict]],
        id_col: str,
    ) -> None:
        with get_conn() as conn:
            for entity_id, score, components in rows:
                conn.execute(
                    f"""
                    INSERT OR REPLACE INTO {table} (run_id, {id_col}, score, components_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    [run_id, entity_id, score, json.dumps(components)],
                )

    def insert_news(self, run_id: str, events: list[dict]) -> None:
        with get_conn() as conn:
            for e in events:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO news_events
                    (id, run_id, source, title, published_at, country_code, severity, risk_type, url, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        e["id"],
                        run_id,
                        e.get("source", ""),
                        e.get("title", ""),
                        parse_published_at(e.get("published_at")),
                        e.get("country_code"),
                        e.get("severity", 1),
                        e.get("risk_type", "general"),
                        e.get("url", ""),
                        json.dumps(e),
                    ],
                )

    def insert_mcdm(self, run_id: str, rows: list[dict]) -> None:
        with get_conn() as conn:
            for r in rows:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO mcdm_scores
                    (run_id, supplier_id, part_id, criterion, raw_value, normalized_value, weight, score, rank)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        run_id,
                        r["supplier_id"],
                        r["part_id"],
                        r["criterion"],
                        r["raw"],
                        r["normalized"],
                        r["weight"],
                        r["score"],
                        r.get("rank"),
                    ],
                )

    def insert_sim_results(self, run_id: str, results: list[dict]) -> None:
        with get_conn() as conn:
            for r in results:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO sim_results (run_id, scenario_id, strategy_id, metrics_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    [run_id, r["scenario_id"], r["strategy_id"], json.dumps(r["metrics"])],
                )

    def insert_recommendations(self, run_id: str, recs: list[dict]) -> None:
        with get_conn() as conn:
            for r in recs:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO recommendations (run_id, part_id, allocation_json, rationale_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    [run_id, r["part_id"], json.dumps(r["allocation"]), json.dumps(r["rationale"])],
                )

    def get_health_all(self) -> list[dict]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT provider, last_ok, last_error, latency_ms, status FROM data_source_health"
            ).fetchall()
        return [
            {
                "provider": r[0],
                "last_ok": r[1].isoformat() if r[1] else None,
                "last_error": r[2],
                "latency_ms": r[3],
                "status": r[4],
            }
            for r in rows
        ]
