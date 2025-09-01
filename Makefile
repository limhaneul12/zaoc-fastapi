# Makefile
PY=uv run
run:
	$(PY) uvicorn app.main:app --reload
lint:
	$(PY) ruff check .
type:
	$(PY) pyright
test:
	$(PY) pytest -q