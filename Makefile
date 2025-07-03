# Manage snailz project.

.DEFAULT: commands

PYTHON = uv run python
PYTHON_M = uv run python -m
SRC = snailz
TESTS = tests
SCRIPT = snailz

## commands: show available commands
commands:
	@grep -h -E '^##' ${MAKEFILE_LIST} | sed -e 's/## //g' | column -t -s ':'

## build: build package
build: clean
	${PYTHON_M} build
	@${PYTHON_M} twine check dist/*

## clean: clean up build artifacts
clean:
	@find . -name '*~' -delete

## coverage: run tests with coverage
coverage:
	${PYTHON_M} coverage run -m pytest tests
	${PYTHON_M} coverage report --show-missing

## docs: generate documentation using MkDocs
.PHONY: docs
docs:
	${PYTHON_M} mkdocs build

## dryrun: run data generation but do not save results
dryrun:
	${SCRIPT} --outdir -

## format: reformat code
format:
	${PYTHON_M} ruff format ${SRC} ${TESTS}

## lint: check the code format and typing
lint:
	${PYTHON_M} ruff check ${SRC} ${TESTS}

## serve: serve documentation website
serve:
	${PYTHON_M} mkdocs serve

## test: run tests
test:
	${PYTHON_M} pytest tests
