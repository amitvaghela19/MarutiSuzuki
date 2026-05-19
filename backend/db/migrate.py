from pathlib import Path

import duckdb

from backend.settings import settings

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def migrate(conn: duckdb.DuckDBPyConnection | None = None) -> duckdb.DuckDBPyConnection:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.cache_dir.mkdir(parents=True, exist_ok=True)
    settings.snapshots_dir.mkdir(parents=True, exist_ok=True)
    own = conn is None
    if own:
        conn = duckdb.connect(str(settings.db_path))
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    for stmt in sql.split(";"):
        s = stmt.strip()
        if s:
            conn.execute(s)
    if own:
        conn.close()
    return conn


if __name__ == "__main__":
    migrate()
    print(f"Migrated: {settings.db_path}")
