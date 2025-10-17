# Tests for Mergington High School Activities API

This directory contains comprehensive tests for the FastAPI application using pytest.

## Test Structure

- **`conftest.py`** - Test configuration and shared fixtures
- **`test_api.py`** - Main API endpoint tests
- **`test_validation.py`** - Data validation and edge case tests

## Running Tests

### Option 1: Using the test runner script (Recommended)
```bash
python run_tests.py
```

### Option 2: Using pytest directly
```bash
# Basic test run
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing

# With HTML coverage report
pytest tests/ --cov=src --cov-report=html
```

## Test Coverage

Current test coverage: **100%** 🎉

The tests cover:
- All API endpoints (`/`, `/activities`, `/activities/{name}/signup`, `/activities/{name}/remove`)
- Error handling and edge cases
- Data validation
- Participant management workflows
- URL encoding and special characters
- Response structure validation

## Test Categories

### API Endpoint Tests (`test_api.py`)
- ✅ Root redirect functionality
- ✅ GET `/activities` - Retrieve all activities
- ✅ POST `/activities/{name}/signup` - Sign up for activities
- ✅ DELETE `/activities/{name}/remove` - Remove participants
- ✅ Error handling (404, 400 errors)
- ✅ Complete signup/removal workflows
- ✅ URL encoding validation

### Data Validation Tests (`test_validation.py`)
- ✅ Data structure validation
- ✅ Participant count consistency
- ✅ Special characters in emails
- ✅ Case sensitivity testing
- ✅ Empty participant lists
- ✅ Concurrent operations
- ✅ Participant uniqueness
- ✅ Long email handling
- ✅ JSON response structure

## Fixtures

### `client`
Standard FastAPI TestClient for synchronous HTTP requests.

### `async_client`
Async HTTP client for testing asynchronous operations.

### `reset_activities` (autouse)
Automatically resets the activities database before each test to ensure test isolation.

### `sample_activity`
Provides sample activity data for testing.

## Dependencies

The following packages are required for testing:
- `pytest` - Testing framework
- `httpx` - HTTP client for FastAPI testing
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting

## Best Practices

1. **Test Isolation** - Each test resets the database state
2. **Comprehensive Coverage** - Tests cover both happy path and error scenarios
3. **Clear Test Names** - Test method names clearly describe what is being tested
4. **Proper Assertions** - Tests verify both success and error responses
5. **Documentation** - Tests serve as living documentation of API behavior

## Adding New Tests

When adding new features to the API:

1. Add positive test cases in `test_api.py`
2. Add negative test cases and edge cases in `test_validation.py`
3. Update fixtures in `conftest.py` if needed
4. Run tests to ensure 100% coverage is maintained

```bash
pytest tests/ --cov=src --cov-report=term-missing
```