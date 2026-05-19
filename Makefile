.PHONY: install migrate dev backend frontend test test-e2e health audit audit-all pins fix-browse plugin-check

install:
	python -m venv .venv
	.venv\Scripts\pip install -e ".[dev]"
	cd frontend && npm install

migrate:
	.venv\Scripts\python -m backend.db.migrate

backend:
	.venv\Scripts\uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo Run 'make backend' and 'make frontend' in two terminals

test:
	.venv\Scripts\pytest backend/tests -q

health:
	.venv\Scripts\python -m backend.scripts.health_check

audit:
	.venv\Scripts\python scripts\security_audit.py

audit-all: audit

pins:
	.venv\Scripts\python scripts\pin_versions.py

fix-browse:
	powershell -ExecutionPolicy Bypass -File scripts\fix_cursor_plugins.ps1

plugin-check:
	powershell -ExecutionPolicy Bypass -File scripts\plugin_alternatives.ps1

test-e2e:
	cd e2e && npm install && npx playwright install chromium && npx playwright test
