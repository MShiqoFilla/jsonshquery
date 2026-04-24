# jsonshquery Test Suite

This directory contains the test suite for the jsonshquery package.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── fixtures/                # Test data files
│   └── test_data.json       # Sample data for testing queries
├── test_core.py             # Unit tests for core functions
├── test_query_models.py     # Tests for query model parsing
├── test_integration.py      # Integration tests for end-to-end functionality
└── README.md                # This file
```

## Running Tests

### Install dependencies
```bash
pip install -e ".[dev]"
```

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_core.py
pytest tests/test_integration.py
```

### Run with coverage
```bash
pytest --cov=jsonshquery --cov-report=html
```

### Run specific test
```bash
pytest tests/test_core.py::test_check_term
pytest tests/test_integration.py::test_simple_term_query
```

### Run tests by marker
```bash
pytest -m unit       # Run only unit tests
pytest -m integration # Run only integration tests
pytest -m "not slow" # Run all tests except slow ones
```

### Verbose output
```bash
pytest -v
pytest -vv  # Very verbose
```

## Test Files

### test_core.py
Tests for core matching functions:
- `check_term`, `check_terms`, `check_match`
- `check_match_phrase`, `check_prefix`, `check_multi_match`
- `check_exists`
- Individual query functions like `query_by_term`, `query_by_match`

### test_query_models.py
Tests for Pydantic query model parsing:
- Match clause parsing
- Term clause parsing
- Bool clause parsing
- Complete ES request body parsing
- Multi-match, prefix, exists clauses

### test_integration.py
End-to-end integration tests:
- Simple term/match queries
- Boolean queries (must, must_not, should)
- Combined boolean logic
- Complex multi-field searches
- All supported query types

## Test Data

The `fixtures/test_data.json` file contains sample data covering:
- Different categories (Electronics, Furniture, Clothing)
- Various field types (string, number, boolean, array)
- Nested objects (address field)
- Different stock statuses
- Multiple tags per product

## Writing New Tests

When adding new features, follow this pattern:

1. **Unit tests** in `test_core.py` for individual functions
2. **Model tests** in `test_query_models.py` for new query types
3. **Integration tests** in `test_integration.py` for end-to-end functionality

Example test:
```python
def test_my_new_feature():
    """Test description"""
    # Setup
    test_data = [...]
    query = {...}
    
    # Execute
    results = search_by_query(test_data, query)
    
    # Assert
    assert len(results) == expected_count
    assert all(condition for doc in results)
```

## Test Coverage Goals

- Core functions: >90% coverage
- Query models: >95% coverage
- Integration tests: Cover all query types and combinations
- Edge cases: Handle null values, missing fields, type mismatches

## Troubleshooting

### Import errors
Make sure to run from project root directory, not inside `tests/` folder.

### Path issues
Tests automatically add `src/` to Python path. If you get import errors, check that the test files have:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
```
