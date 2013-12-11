.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "testall - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

devinstall:
	pip install -e .[tox]
	pip install -e .[docs]
	pip install -e .[tests]

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 zing tests

test:
	python setup.py test

test-all:
	tox

coverage:
	coverage run --source zing setup.py test
	coverage report -m
	coverage html
	@echo "Open htmlcov/index.html to see report"

docs:
	rm -f docs/zing.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ zing
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html
