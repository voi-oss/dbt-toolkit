APP_NAME?=dbt-toolkit
REGISTRY?=eu.gcr.io/voi-data-warehouse
IMAGE=$(REGISTRY)/$(APP_NAME)
SHORT_SHA?=$(shell git rev-parse --short HEAD)
VERSION?=$(SHORT_SHA)

.PHONY: build
build: clean-build
	python3 setup.py sdist bdist_wheel

.PHONY: clean-build
clean-build:
	rm -rf build dist

.PHONY: install-dev
install-dev:
	@echo "Installing it locally with editable mode"
	@pip install -e .

.PHONY: type
type:
	@echo "Running mypy"
	@pipenv run mypy .

.PHONY: check-lint
check-lint:
	@echo "Running isort"
	@pipenv run isort --check-only .
	@echo "Running black"
	@pipenv run black --check .
	@echo "Running flake"
	@pipenv run flake8

.PHONY: lint
lint:
	@echo "Running isort"
	@pipenv run isort .
	@echo "Running black"
	@pipenv run black .
	@echo "Running flake"
	@pipenv run flake8

.PHONY: test
test:
	@pipenv run pytest tests/

.PHONY: test-coverage
test-coverage:
	@pipenv run pytest tests/ --cov=dbttoolkit --cov-report=xml
