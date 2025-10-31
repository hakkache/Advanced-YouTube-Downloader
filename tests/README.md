# Test Suite for Advanced YouTube Downloader

This directory contains the test suite for the Advanced YouTube Downloader application.

## Running Tests

### Prerequisites
```bash
pip install pytest pytest-cov
```

### Run All Tests
```bash
# From project root
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=app --cov=scheduler_service
```

### Run Specific Tests
```bash
# Run basic tests only
python -m pytest tests/test_basic.py

# Run with verbose output
python -m pytest tests/ -v
```

## Test Structure

- `test_basic.py` - Basic functionality tests
  - Import tests
  - URL validation
  - Time parsing
  - File structure validation
  - Mock tests for video info retrieval

## Adding New Tests

When adding new features, please include corresponding tests:

1. **Unit Tests** - Test individual functions
2. **Integration Tests** - Test feature workflows
3. **Mock Tests** - Test external API interactions

### Example Test
```python
def test_new_feature(self):
    """Test description."""
    # Arrange
    input_data = "test_input"
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    self.assertEqual(result, expected_output)
```

## Test Guidelines

- Use descriptive test names
- Include docstrings for test methods
- Mock external dependencies (yt-dlp, file system, network)
- Test both success and failure cases
- Keep tests independent and isolated

## Coverage Goals

- Aim for >80% code coverage
- Focus on critical functionality
- Test error handling paths
- Include edge cases

## Continuous Integration

Tests run automatically on:
- Pull requests to main branch
- Pushes to main and develop branches
- Python versions: 3.8, 3.9, 3.10, 3.11, 3.12