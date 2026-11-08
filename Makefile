.PHONY: tables test
tables:
	python -m src.build_tables
test:
	pytest -q
	