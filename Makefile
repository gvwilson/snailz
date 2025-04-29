# Manage snailz project.

.DEFAULT: commands

BUILD = build
DATA = data
SCRIPTS = scripts

PARAMS = params.json
ZIPFILE = snailz.zip

PYTHON = uv run python
PYTHON_M = uv run python -m
SNAILZ = uv run snailz

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
	@rm -rf ${PARAMS} ${DATA} ${BUILD}

## coverage: run tests with coverage
coverage:
	${PYTHON_M} coverage run -m pytest tests
	${PYTHON_M} coverage report --show-missing

## data: rebuild all data
.PHONY: data
data:
	@rm -rf ${DATA}
	${SNAILZ} --defaults > ${PARAMS}
	${SNAILZ} --params ${PARAMS} --outdir ${DATA}

## docs: generate documentation using MkDocs
.PHONY: docs
docs:
	${PYTHON_M} mkdocs build

## format: reformat code
format:
	${PYTHON_M} ruff format .

## lint: check the code format and typing
lint:
	${PYTHON_M} ruff check .

## profile: run with profiling and show top 20 time-consuming functions
profile:
	@mkdir -p ${DATA}
	${PYTHON_M} cProfile -s tottime scripts/profiling.py | head -n 30

## publish: publish package (needs TOKEN defined on command line)
publish:
	${PYTHON_M} twine upload --verbose -u __token__ -p ${TOKEN} dist/*

## site: serve documentation website
site:
	${PYTHON_M} mkdocs serve

## test: run tests
test:
	${PYTHON_M} pytest tests

## zip: create ZIP file from generated data
zip:
	${SNAILZ} zip --data ${DATA} --output ${ZIPFILE}
