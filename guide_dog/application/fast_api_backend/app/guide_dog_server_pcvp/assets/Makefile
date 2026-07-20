LINT_PATHS=application/

test:
	python3 -m pytest --cov-report term --color=yes --cov=. --cov-report html -v && \
	python3 -m http.server 8004 -d htmlcov/

mypy:
	mypy ${LINT_PATHS}

lint:
	# stop the build if there are Python syntax errors or undefined names
	# see https://www.flake8rules.com/
	# ruff ${LINT_PATHS} --select=E9,F63,F7,F82 --show-source
	#ruff check . --show-settings
	ruff check $(LINT_PATHS) --select=E9,F63,F7,F82 --show-files
	# exit-zero treats all errors as warnings.
	ruff check ${LINT_PATHS} --exit-zero

format:
	# Sort imports
	isort ${LINT_PATHS}
	# Reformat using black
	black ${LINT_PATHS}

check-codestyle:
	# Sort imports
	isort --check ${LINT_PATHS}
	# Reformat using black
	black --check ${LINT_PATHS}

commit-checks:  mypy lint format check-codestyle


all: mypy lint format check-codestyle test

.PHONY: lint format check-codestyle commit-checks
