# Contributing to Witch Doctor

Thank you for your interest in contributing! This document covers how to set up the project locally, run tests, and submit changes.

## Getting started

You'll need Python 3.10+ and [Poetry](https://python-poetry.org/docs/#installation).

```bash
git clone https://github.com/CenturyBoys/witch-doctor.git
cd witch-doctor
poetry install
```

## Running tests

```bash
poetry run pytest tests/ -v
```

To run benchmarks:

```bash
poetry run pytest tests/test_benchmarks.py --benchmark-only
```

To check test coverage:

```bash
poetry run pytest tests/ --cov=witch_doctor
```

## Linting

The project uses [Ruff](https://docs.astral.sh/ruff/) for linting. Run it before submitting:

```bash
poetry run ruff check .
```

Pre-commit hooks are configured to run Ruff automatically on each commit. Install them once with:

```bash
poetry run pre-commit install
```

## Making changes

- Keep changes focused — one bug fix or feature per pull request.
- Add or update tests to cover your change. The project uses `pytest` and maintains test isolation via a `_reset()` fixture in `conftest.py`.
- Update `CHANGELOG.md` under an `[Unreleased]` section following the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
- All code must pass linting and the full test suite before merging.

## Submitting a pull request

1. Fork the repository and create a branch from `main`.
2. Make your changes, ensuring tests pass and linting is clean.
3. Open a pull request against `main` with a clear description of what changed and why.

## Reporting bugs

Open an issue at [github.com/CenturyBoys/witch-doctor/issues](https://github.com/CenturyBoys/witch-doctor/issues). Include a minimal reproducible example, the Python version, and the installed package version.

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
