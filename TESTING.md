# Testing Guide

## Overview

This repository has a comprehensive test suite with 97% code coverage, consisting of 58 tests organized into four categories:

- **Smoke Tests**: Basic tests to verify the test harness is working
- **Unit Tests**: Tests for individual functions and business logic
- **Integration Tests**: Tests for file operations and PDF manipulation
- **Characterization Tests**: Black-box tests for CLI behavior
- **Edge Case Tests**: Tests for error handling and unusual inputs

## Running Tests

### Prerequisites

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest tests/
```

### Run Tests with Coverage

```bash
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html
```

Open `htmlcov/index.html` in a browser to view detailed coverage report.

### Run Specific Test Categories

```bash
# Smoke tests
pytest tests/ -m smoke

# Unit tests
pytest tests/ -m unit

# Integration tests
pytest tests/ -m integration

# Characterization tests
pytest tests/ -m characterization

# Edge case tests
pytest tests/ -m edge_case
```

### Run Specific Test Files

```bash
pytest tests/test_unit.py -v
pytest tests/test_integration.py -v
pytest tests/test_edge_cases.py -v
pytest tests/test_characterization.py -v
```

## Test Organization

### tests/test_smoke.py
Basic smoke tests to ensure:
- pytest is configured correctly
- required dependencies can be imported

### tests/test_unit.py
Unit tests for individual functions:
- `read_config()`: Reading and parsing YAML configuration
- `parse_args()`: Command-line argument parsing
- `apply_writer_compression()`: PDF compression logic

### tests/test_integration.py
Integration tests with real file operations:
- `extract_songs_from_pdf()`: Extracting pages from PDFs
- `compile_directory()`: Compiling multiple PDFs into one
- `compile_directories()`: Batch compilation
- File creation, directory creation, and PDF manipulation

### tests/test_characterization.py
Black-box tests that capture current CLI behavior:
- Help output
- Split mode with various configurations
- Compile mode with various options
- Logging levels

### tests/test_edge_cases.py
Tests for edge cases and error handling:
- Empty inputs
- Invalid page ranges
- Non-existent files
- Malformed configurations
- Special characters in filenames
- Unicode handling
- Case-insensitive sorting

## Test Fixtures

Common test fixtures are defined in `tests/conftest.py`:

- `temp_dir`: Temporary directory for test files
- `sample_pdf`: 5-page PDF for testing
- `multi_page_pdf`: 10-page PDF for testing
- `empty_pdf`: PDF with no pages
- `sample_config_yaml`: Sample configuration file
- `directory_with_pdfs`: Directory with multiple PDFs for compilation

## Known Issues

The test suite documents several known issues in the current implementation:

1. **UnboundLocalError in `read_config()`**
   - When a non-existent or malformed config file is read, `read_config()` raises `UnboundLocalError` instead of a more graceful error
   - Tests: `test_read_nonexistent_config`, `test_read_malformed_yaml`

2. **No filename sanitization**
   - Song names with filesystem-incompatible characters (/, \, :, ?) cause `FileNotFoundError`
   - Test: `test_extract_with_special_characters_in_name`

3. **Missing required fields cause KeyError**
   - Config files missing required fields (`file`, `offset`, `songs`) raise `KeyError`
   - Tests: `test_config_with_missing_*` series

These are preserved to maintain backward compatibility and are explicitly documented in test docstrings.

## Continuous Integration

Tests run automatically on GitHub Actions for:
- All pushes to main/master branches
- All pull requests
- Python versions: 3.9, 3.10, 3.11, 3.12

See `.github/workflows/test.yml` for CI configuration.

## Coverage Report

Current coverage: **97%**

Uncovered lines are primarily:
- The `if __name__ == "__main__"` block
- Some error handling paths for external service failures
- Compression fallback logic for edge cases

## Adding New Tests

When adding new features:

1. Add fixtures to `tests/conftest.py` if needed
2. Add unit tests for new functions in `tests/test_unit.py`
3. Add integration tests for file operations in `tests/test_integration.py`
4. Add characterization tests for CLI changes in `tests/test_characterization.py`
5. Add edge case tests in `tests/test_edge_cases.py`
6. Use appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`, etc.)

Example:

```python
@pytest.mark.unit
def test_new_function():
    """Test description."""
    result = new_function(input)
    assert result == expected
```

## Code Quality

The project uses:
- **black**: Code formatting
- **flake8**: Linting
- **isort**: Import sorting

Run all checks:

```bash
black --check split-real-books.py tests/
flake8 split-real-books.py tests/ --max-line-length=88 --extend-ignore=E203
isort --check-only --profile black split-real-books.py tests/
```

Or use pre-commit hooks:

```bash
pre-commit install
pre-commit run --all-files
```
