# split-real-books

Simple script to split pdf files (in my use-case real books) into multiple
files thanks to a configuration file. It can now also compile the generated
PDFs into a single song book with a convenient table of contents.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

For development (including testing):

```bash
pip install -r requirements-dev.txt
```

# Configuration

Check `config.example.yaml` for the configuration format.

# Usage

## Split PDFs based on the configuration

```
python split-real-books.py
```

## Compile the generated PDFs into a single book

Once the songs have been extracted you can merge the PDFs that live in an
output folder (for example `output_songs`) into a single lightweight PDF with
an automatically generated table of contents:

```
python split-real-books.py --compile-directory output_songs --compress
```

The command above creates `CombinedRealBook.pdf` in `output_songs/`. Every song
is listed alphabetically in the PDF outline so you can quickly jump to any
sheet. The optional `--compress` flag applies additional stream compression to
keep the resulting file small enough for mobile use.

If you run the splitter against a configuration that contains several
`output_directory` entries, you can automatically compile each of them right
after the split with:

```
python split-real-books.py --compile-from-config
```

Additional options:

- `--compiled-filename`: customise the name of the merged PDF (defaults to
  `CombinedRealBook.pdf`).
- `--compile-directory`: can be passed multiple times to merge several folders
  in one run.
- `--compress`: reduce the size of the generated compilation by compressing the
  internal PDF streams.

## Testing

This project has a comprehensive test suite with 97% code coverage.

### Running Tests

Run all tests:

```bash
pytest tests/
```

Run tests with coverage report:

```bash
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html
```

Run specific test categories:

```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests only
pytest tests/ -m integration

# Characterization tests only
pytest tests/ -m characterization

# Edge case tests only
pytest tests/ -m edge_case
```

### Test Structure

- **tests/test_smoke.py**: Basic smoke tests to verify the test harness
- **tests/test_unit.py**: Unit tests for individual functions (argument parsing, config reading, compression)
- **tests/test_integration.py**: Integration tests with real file operations and PDF manipulation
- **tests/test_characterization.py**: Black-box tests for CLI entry points to capture current behavior
- **tests/test_edge_cases.py**: Edge cases and error handling tests

### Known Issues

The test suite documents current behavior including some known issues:

1. **UnboundLocalError in `read_config()`**: When reading a non-existent or malformed config file, the function raises `UnboundLocalError` instead of a more graceful error.
2. **No filename sanitization**: Song names with filesystem-incompatible characters (like `/`, `\`, `:`, `?`) will cause `FileNotFoundError`.
3. **Missing required fields**: Config files missing required fields (`file`, `offset`, `songs`) will raise `KeyError`.

These behaviors are preserved to maintain backward compatibility and are documented in the tests.

## Development

### Linting

The project uses pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Linters used:
- **black**: Code formatting
- **flake8**: Linting
- **isort**: Import sorting

### Continuous Integration

GitHub Actions automatically runs tests on Python 3.9, 3.10, 3.11, and 3.12 for all pull requests and pushes to main/master branches.
