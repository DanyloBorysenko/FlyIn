UV := uv
SRC := src
DEB := pdb
PY := $(UV) run python3

install: .venv/.installed

.venv/.installed: uv.lock pyproject.toml
	$(UV) sync --group dev
	@touch $@

run: .venv/.installed
	$(PY) -m $(SRC)

debug: .venv/.installed
	$(PY) -m $(DEB) -m $(SRC)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

fclean: clean
	rm -rf .venv

re: fclean install

lint: .venv/.installed
	$(UV) run flake8 .
	$(UV) run mypy . \
	    --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

.PHONY: install run debug clean lint fclean re
