SIMULTANEOUS_TEST_JOBS=4

install-deps: deps
	pip-sync requirements.txt

deps:
	python -m pip install --upgrade pip pip-tools
	pip-compile --output-file requirements.txt --resolver=backtracking pyproject.toml

install-dev-deps: dev-deps
	pip-sync requirements.txt dev-requirements.txt

dev-deps: deps
	pip-compile --extra=dev --output-file dev-requirements.txt --resolver=backtracking pyproject.toml

format:
	cd src && ruff check --select F401 --fix .
	cd src && ruff check --select I --fix .
	cd src && ruff format .

lint:
	cd src && ruff check .
	mypy src

test:
	pytest -n ${SIMULTANEOUS_TEST_JOBS} --cov=. --ff --cov-report=term-missing
	pytest --dead-fixtures
