# Contributing to CFO Bot

Thank you for your interest in contributing to CFO Bot! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Release Process](#release-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.9+ (3.10+ recommended)
- Git
- Docker (optional, for containerized development)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/cfobot.git
   cd cfobot
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/original-org/cfobot.git
   ```

## Development Setup

### Option 1: Local Development

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

4. **Run tests to verify setup:**
   ```bash
   pytest
   ```

### Option 2: Docker Development

1. **Build the development image:**
   ```bash
   docker-compose build cfobot-dev
   ```

2. **Run tests:**
   ```bash
   docker-compose --profile test run cfobot-test
   ```

3. **Run linting:**
   ```bash
   docker-compose --profile lint run cfobot-lint
   ```

4. **Run type checking:**
   ```bash
   docker-compose --profile typecheck run cfobot-typecheck
   ```

## Code Style Guidelines

### Python Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

### Formatting

All code is automatically formatted with Black. Run before committing:

```bash
black cfobot tests
isort cfobot tests
```

### Type Hints

- Use Python 3.10+ type hints (`list[str]` instead of `List[str]`)
- Use `|` instead of `Union` for union types
- All public functions must have type hints
- Use `from __future__ import annotations` for forward references

### Docstrings

Use Google-style docstrings for all public functions:

```python
def calculate_ebitda(data: FinancialData) -> float:
    """Calculate EBITDA from financial data.
    
    Args:
        data: Financial data containing income statement and ERI
        
    Returns:
        Calculated EBITDA value
        
    Raises:
        ValueError: If required data is missing
        
    Examples:
        >>> data = load_financial_data(...)
        >>> ebitda = calculate_ebitda(data)
        >>> print(f"EBITDA: ${ebitda:,.0f}")
    """
```

### Naming Conventions

- **Functions and variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private functions**: `_leading_underscore`

### File Organization

```
cfobot/
├── __init__.py
├── cli.py              # Command-line interface
├── config.py           # Configuration management
├── constants.py        # Application constants
├── data_loader.py      # Data loading utilities
├── emailer.py          # Email functionality
├── processing.py       # Core business logic
├── reporting.py        # Report generation
├── templates.py        # Email templates
└── validators.py       # Data validation
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/               # Unit tests
│   ├── test_processing.py
│   ├── test_validators.py
│   └── test_emailer.py
├── integration/        # Integration tests
│   └── test_pipeline.py
└── fixtures/           # Test data
    └── sample_data.py
```

### Writing Tests

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test complete workflows
3. **Fixtures**: Use pytest fixtures for reusable test data
4. **Mocks**: Mock external dependencies (SMTP, file system)

### Test Coverage

- Maintain >80% test coverage
- All new code must have tests
- Use `pytest-cov` to check coverage:
  ```bash
  pytest --cov=cfobot --cov-report=html
  ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cfobot --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_processing.py

# Run with verbose output
pytest -v
```

## Pull Request Process

### Before Submitting

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Add tests** for new functionality

4. **Update documentation** if needed

5. **Run all checks:**
   ```bash
   # Format code
   black cfobot tests
   isort cfobot tests
   
   # Run linting
   flake8 cfobot tests
   
   # Run type checking
   mypy cfobot
   
   # Run tests
   pytest --cov=cfobot --cov-fail-under=80
   ```

6. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

### Commit Message Format

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

### Pull Request Template

When creating a PR, include:

1. **Description** of changes
2. **Type of change** (bug fix, feature, etc.)
3. **Testing** - how you tested the changes
4. **Checklist** - ensure all requirements are met
5. **Screenshots** if applicable

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by maintainers
3. **Testing** in different environments
4. **Documentation** review

## Issue Reporting

### Bug Reports

When reporting bugs, include:

1. **Environment details** (OS, Python version, etc.)
2. **Steps to reproduce** the issue
3. **Expected behavior** vs actual behavior
4. **Error messages** and logs
5. **Sample data** if applicable

### Feature Requests

For new features, include:

1. **Use case** and motivation
2. **Proposed solution** or design
3. **Alternatives** considered
4. **Impact** on existing functionality

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with new features/fixes
3. **Run full test suite** locally
4. **Create release branch** from main
5. **Tag the release** with version number
6. **Create GitHub release** with changelog
7. **Publish to PyPI** (automated via CI/CD)

## Development Workflow

### Daily Workflow

1. **Pull latest changes:**
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Make changes** and test locally

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature
   ```

5. **Create pull request** on GitHub

### Code Review Guidelines

**For Reviewers:**
- Check code quality and style
- Verify tests are adequate
- Ensure documentation is updated
- Test the changes locally if needed

**For Authors:**
- Respond to feedback promptly
- Make requested changes
- Update tests if needed
- Keep PR focused and small

## Getting Help

- **Documentation**: Check the README and code comments
- **Issues**: Search existing issues or create new ones
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Ask questions in PR comments

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to CFO Bot! 🚀
