.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 aws_cfn_resources_schemas tests

test: ## run tests quickly with the default Python
	pytest -svx tests/

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source aws_cfn_resources_schemas --source aws_cfn_resources_schemas -m pytest tests
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/aws_cfn_resources_schemas.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ aws_cfn_resources_schemas
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

conform	: ## Conform to a standard of coding syntax
	isort --profile black aws_cfn_resources_schemas
	black aws_cfn_resources_schemas tests
	find aws_cfn_resources_schemas -name "*.json" -type f  -exec sed -i '1s/^\xEF\xBB\xBF//' {} +


python39	: clean
			test -d layer && rm -rf layer || mkdir layer
			docker run -u $(shell bash -c 'id -u'):$(shell bash -c 'id -u') \
			--rm -it -v $(PWD):/app --entrypoint /bin/bash \
			public.ecr.aws/compose-x/python:3.9 \
			-c "pip install --no-cache-dir /app/dist/*.whl -t /app/layer"

python38	: clean
			test -d layer && rm -rf layer || mkdir layer
			docker run -u $(shell bash -c 'id -u'):$(shell bash -c 'id -u') \
			--rm -it -v $(PWD):/app/ --entrypoint /bin/bash \
			public.ecr.aws/compose-x/python:3.8 \
			-c "pip install --no-cache-dir /app/dist/*.whl -t /app/layer"

python37	: clean
			test -d layer && rm -rf layer || mkdir layer
			docker run -u $(shell bash -c 'id -u'):$(shell bash -c 'id -u') \
			--rm -it -v $(PWD):/app/ --entrypoint /bin/bash \
			public.ecr.aws/compose-x/python:3.7 \
			-c "ls dist ; pip install --no-cache-dir /app/dist/*.whl -t /opt/layer"


dist:		clean ## builds source and wheel package
			poetry build

package:	dist $(PYTHON_VERSION)

layer		: package python39
