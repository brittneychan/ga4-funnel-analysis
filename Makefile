.PHONY: tables test
tables:
	python -m src.build_tables
test:
	python -m pytest -q
	