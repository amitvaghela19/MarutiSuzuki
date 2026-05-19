"""CLI: python -m backend.scripts.health_check"""
import asyncio
import json

from backend.config.loader import load_config
from backend.db.migrate import migrate
from backend.db.repository import Repository
from backend.ingestion.orchestrator import run_ingestion


async def main():
    migrate()
    cfg = load_config()
    repo = Repository()
    data, news = await run_ingestion(cfg, repo)
    print(json.dumps({"health": data.get("health"), "news_count": len(news)}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
