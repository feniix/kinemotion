# Backend API Tests

Comprehensive pytest test suite for the Kinemotion backend API (Issue #12).

## Overview

**Total Tests:** 86
**Passing:** 78+
**Coverage Areas:** Health checks, API endpoints, input validation, error handling, R2 integration

## Test Files

### 1. `test_health.py` (8 tests)

Tests the `/health` endpoint health check functionality.

**Coverage:**

- Returns 200 status code
- Response structure and required fields
- Status value is "ok"
- Service name is correct
- Version field present
- Timestamp in ISO format
- R2 configured boolean flag
- Multiple sequential calls

### 2. `test_api_endpoints.py` (18 tests)

Tests the main `/api/analyze` endpoint with both CMJ and Drop Jump analysis.

**Coverage:**

- CMJ video analysis (200 response, metrics structure, expected fields)
- Drop Jump video analysis (200 response, metrics structure, expected fields)
- Response structure validation (status, message, metrics, processing_time_s)
- Processing time recording
- Quality presets (default "balanced", custom "fast"/"accurate")
- Message contains jump type
- Metrics contain expected fields
- File extensions (.mp4, .mov, .avi)
- Default jump type (CMJ)
- Results URL handling without R2

**Example Test:**

```python
def test_analyze_cmj_video_returns_200(client, sample_video_bytes):
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})
    assert response.status_code == 200
```

### 3. `test_validation.py` (31 tests)

Tests file and input validation for the analysis endpoint.

**File Size Validation:**

- Files under 500MB accepted
- Files over 500MB rejected with 422 error

**Format Validation:**

- Accepted formats: .mp4, .mov, .avi, .mkv, .flv, .wmv
- Rejected formats: .txt, .jpg, .pdf, .zip (and any non-video)
- Files without extension rejected
- Files without filename rejected

**Jump Type Validation:**

- Valid types: "cmj", "drop_jump"
- Invalid types rejected with 422
- Case-insensitive (CMJ, DROP_JUMP accepted)
- Default type: "cmj" when omitted

**Quality Preset Validation:**

- Accepted: "fast", "balanced", "accurate"
- Default: "balanced"

**Example Test:**

```python
def test_file_size_over_limit_rejected(client, large_video_bytes):
    files = {"file": ("large.mp4", BytesIO(large_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})
    assert response.status_code == 422
    assert "500MB" in response.json()["error"]
```

### 4. `test_error_handling.py` (14 tests)

Tests error handling for various failure scenarios.

**Error Response Validation:**

- Invalid file format → 422 with error details
- Invalid jump_type → 422 with error details
- File too large → 422 with error details
- Processing error → 500 with error details
- ValueError during processing → 422
- Generic exceptions → 500

**Response Format:**

- Status code matches error type (422 for validation, 500 for processing)
- All responses include: status, message, error, processing_time_s
- Error messages are descriptive
- No metrics in error responses

**File Cleanup:**

- Temporary files cleaned up after processing errors
- Temporary files cleaned up after validation errors
- Multiple sequential errors handled correctly

**Example Test:**

```python
def test_kinemotion_processing_error_returns_500(client, sample_video_bytes):
    with patch("kinemotion_backend.app.process_cmj_video") as mock:
        mock.side_effect = RuntimeError("Processing failed")
        files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
        response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})
        assert response.status_code == 500
```

### 5. `test_r2_integration.py` (15 tests)

Tests R2 storage client initialization and file operations (mocked).

**R2 Client Initialization:**

- Requires endpoint, access key, secret key
- Optional bucket name (defaults to "kinemotion")
- Raises ValueError if credentials missing
- Uses S3-compatible boto3 client with "auto" region

**File Operations (Mocked):**

- Upload file with error handling
- Upload returns proper S3 URL
- Download file with error handling
- Delete file with error handling
- Put object (for JSON results) with error handling

**Graceful Degradation:**

- Endpoint works without R2 credentials
- R2 upload failure returns 500
- R2 results upload failure doesn't crash (graceful degradation)

**Example Test:**

```python
def test_r2_client_initialization_with_credentials():
    with patch.dict("os.environ", {
        "R2_ENDPOINT": "https://r2.example.com",
        "R2_ACCESS_KEY": "test_key",
        "R2_SECRET_KEY": "test_secret",
    }):
        client = R2StorageClient()
        assert client.endpoint == "https://r2.example.com"
```

## Fixtures (`conftest.py`)

### Core Fixtures

**`client`** - FastAPI TestClient

```python
@pytest.fixture
def client():
    return TestClient(app)
```

**`sample_cmj_metrics`** - Sample CMJ analysis results

```python
{
    "jump_height": 0.42,
    "flight_time": 0.825,
    "countermovement_depth": 0.35,
    # ... more fields
}
```

**`sample_dropjump_metrics`** - Sample Drop Jump analysis results

```python
{
    "ground_contact_time": 0.285,
    "flight_time": 0.515,
    "jump_height": 1.3,
    # ... more fields
}
```

**`sample_video_bytes`** - Minimal valid MP4 file bytes

```python
# Binary MP4 data for testing file uploads
```

**`large_video_bytes`** - 501MB of data (for size validation)

**`invalid_video_bytes`** - Text file data (for format validation)

**`mock_kinemotion_analysis`** (autouse) - Auto-patches kinemotion analysis functions

- Returns sample metrics for all tests
- Can be overridden per-test with `patch()`

**`clear_r2_client`** (autouse) - Clears R2 client before each test

**`no_r2_env`** - Unsets R2 environment variables

**`temp_video_file`** - Creates temporary video file in tmp_path

### Mock Fixture Example

```python
@pytest.fixture
def mock_kinemotion_analysis(sample_cmj_metrics, sample_dropjump_metrics):
    """Mock both analysis functions for all tests."""
    with patch("kinemotion_backend.app.process_cmj_video") as mock_cmj, \
         patch("kinemotion_backend.app.process_dropjump_video") as mock_dj:
        # Returns CMJ metrics
        # Returns Drop Jump metrics
        yield
```

## Running Tests

### All Tests

```bash
uv run --directory backend pytest
```

### Specific Test File

```bash
uv run --directory backend pytest tests/test_health.py -v
```

### Specific Test

```bash
uv run --directory backend pytest tests/test_health.py::test_health_check_returns_200 -v
```

### With Coverage Report

```bash
uv run --directory backend pytest --cov=kinemotion_backend --cov-report=html
```

### Watch Mode (if pytest-watch installed)

```bash
uv run --directory backend ptw tests/
```

## Test Patterns Used

### 1. AAA Pattern (Arrange, Act, Assert)

```python
def test_example(client, sample_video_bytes):
    # Arrange
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}

    # Act
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    # Assert
    assert response.status_code == 200
```

### 2. Context Manager for Mocking

```python
with patch("kinemotion_backend.app.process_cmj_video") as mock_cmj:
    mock_cmj.return_value = MockResult()
    response = client.post(...)
    mock_cmj.assert_called_once()
```

### 3. Parameterization for Multiple Formats

```python
@pytest.mark.parametrize("format_ext", [".mp4", ".mov", ".avi"])
def test_format_accepted(client, sample_video_bytes, format_ext):
    files = {"file": (f"test{format_ext}", ...)}
    response = client.post(...)
    assert response.status_code == 200
```

## Key Test Scenarios

### Happy Path

- CMJ analysis with valid video → returns metrics
- Drop Jump analysis with valid video → returns metrics
- Response has correct structure and all required fields
- Processing time is recorded

### Validation Errors (422)

- Invalid file format (.txt, .jpg, etc.)
- Invalid jump_type ("invalid")
- File too large (>500MB)
- Missing or empty filename

### Processing Errors (500)

- Video processing fails (RuntimeError, etc.)
- Generic exceptions
- KeyboardInterrupt

### Edge Cases

- Empty files
- Multiple sequential requests
- R2 degradation (works without credentials)
- Various file extensions

## Mocking Strategy

### Why Mock Kinemotion?

- Kinemotion analysis requires actual video parsing (slow, complex)
- MediaPipe pose detection requires ML models
- Real video files are large
- Tests should be fast and deterministic

### Mocking Approach

```python
# Auto-use fixture mocks both analysis functions
@pytest.fixture(autouse=True)
def mock_kinemotion_analysis(...):
    with patch("kinemotion_backend.app.process_cmj_video") as mock_cmj:
        mock_cmj.return_value = MockResult()
        yield

# Per-test override for specific behavior
with patch("kinemotion_backend.app.process_cmj_video") as mock:
    mock.side_effect = RuntimeError("...")
    # test error handling
```

## Coverage Notes

**High Coverage Areas:**

- Health check endpoint: 100%
- Input validation: ~95%
- Error handling: ~90%
- API response structure: ~95%

**Lower Coverage Areas:**

- Actual kinemotion integration (intentionally mocked)
- R2 upload/download (mocked with boto3)
- Real video processing (requires actual videos)
- Edge cases with corrupt video files

## Known Limitations

1. **Real Video Processing** - Tests mock kinemotion analysis. For real video testing, use the main project's test videos.
1. **R2 Credentials** - R2 client tests are fully mocked. Integration requires real R2 credentials.
1. **MediaPipe** - Pose tracking is mocked. Real testing requires actual videos.
1. **Large Files** - 501MB test fixture uses memory. Could be optimized with temp file generation.

## Maintenance Notes

### Adding New Tests

1. Use AAA pattern (Arrange, Act, Assert)
1. Include descriptive docstrings
1. Use existing fixtures when possible
1. Mock external dependencies
1. Test both happy path and error cases

### Updating Fixtures

When kinemotion metrics change:

1. Update `sample_cmj_metrics` and `sample_dropjump_metrics` in `conftest.py`
1. Run all tests to verify
1. Update test assertions if needed

### Debugging Failed Tests

```bash
# Show full traceback
uv run --directory backend pytest tests/test_file.py -vv --tb=long

# Drop into debugger on failure
uv run --directory backend pytest tests/test_file.py --pdb

# Show print statements
uv run --directory backend pytest tests/test_file.py -s
```

## CI/CD Integration

These tests run in GitHub Actions on every push and PR. See `.github/workflows/test.yml`.

**Test Command:**

```bash
uv run pytest backend/tests/
```

**Coverage Upload:**

- Runs with coverage collection
- Uploads to SonarQube Cloud
- Requires SONAR_TOKEN secret

## References

- FastAPI Testing: https://fastapi.tiangolo.com/advanced/testing-dependencies/
- Pytest Documentation: https://docs.pytest.org/
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html
