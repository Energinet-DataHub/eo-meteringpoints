# Development Environment

## Getting Started

### Installation options
The list below shows a few different ways to get the development environment up and running.

- [VSCode using devcontainers](../vscode/README.md)


## Run tests

Run unit- and integration tests.

### All tests

    $ pipenv run python -m pytest ../tests/

### Integration test:

    $ pipenv run unittest

### Unit test:

    $ pipenv run integrationtest

## Run linting:

Run PEP8 linting:

    $ pipenv run lint-flake8
