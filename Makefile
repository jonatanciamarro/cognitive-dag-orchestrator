.PHONY: setup test run dashboard docker deploy clean

setup:
	@bash scripts/setup.sh

test:
	.venv/bin/python -m unittest discover tests/ -v

run:
	.venv/bin/python scripts/autopilot.py \
		--workflow workflows/revenue_workflow.json \
		--context examples/content_workflow_context.json \
		--db .state/autopilot.db

loop:
	.venv/bin/python scripts/autopilot.py \
		--workflow workflows/revenue_workflow.json \
		--context examples/content_workflow_context.json \
		--db .state/autopilot.db \
		--loop --interval 48

stats:
	.venv/bin/python scripts/autopilot.py \
		--workflow workflows/revenue_workflow.json \
		--context examples/content_workflow_context.json \
		--db .state/autopilot.db --stats

dashboard:
	.venv/bin/streamlit run dashboard/app.py

docker:
	docker-compose up -d --build

deploy:
	@bash scripts/deploy.sh

clean:
	rm -rf .state/ output/ reports/ __pycache__/ .venv/
	rm -f *.sqlite3
	@echo "✅ Limpo"

all: setup test run
