# Contributing to apinator-server

## Development Setup

```bash
git clone https://github.com/apinator-io/sdk-python.git
cd sdk-python
pip install -e ".[dev]"
pytest tests/ -v
```

## Code Standards

- Python 3.10+ with full type hints (`from __future__ import annotations`)
- Zero external dependencies — stdlib only
- All public functions and methods must have docstrings
- 85%+ test coverage

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=apinator --cov-report=term-missing

# Run a single test file
pytest tests/test_client.py -v
```

## Commit Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add batch event triggering
fix: correct HMAC signature for empty body
docs: update webhook verification example
test: add coverage for channel auth edge cases
chore: update pytest to v8
```

## Pull Request Process

1. Fork the repo and create a feature branch from `main`
2. Write tests for any new functionality
3. Run the test suite: `pytest tests/ -v`
4. Update documentation if you changed public APIs
5. Submit a PR with a clear description of what and why

## Reporting Issues

Use [GitHub Issues](https://github.com/apinator-io/sdk-python/issues) with the provided templates.
